# TaskFlow Phase 5: 依赖关系完善

> **版本**: 5.0.0  
> **阶段**: Phase 5 - 批量设置 + 依赖面板  
> **更新**: 2026-03-05

## 1. 概述

在 Phase 4 基础上完善依赖关系功能：
- 批量设置前置任务（一次为多个任务设置共同前置任务）
- 依赖面板（任务详情页双向查看依赖关系）

## 2. 数据库

```sql
-- task_dependencies 表（新增）
CREATE TABLE IF NOT EXISTS task_dependencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,           -- 依赖方（被阻塞的任务）
    depends_on_id INTEGER NOT NULL,     -- 被依赖方（前置任务）
    dependency_type TEXT DEFAULT 'requires', -- requires: 必须完成
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (depends_on_id) REFERENCES tasks(id) ON DELETE CASCADE,
    UNIQUE(task_id, depends_on_id)
);

-- 旧 task_links 表（如果还存在则删除）
DROP TABLE IF EXISTS task_links;
```

**说明**：
- 一个任务可以有多个前置任务（1:N）
- 所有前置任务都完成，才解除阻塞（AND 关系）

## 3. API 设计

### 3.1 依赖关系接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/tasks/{id}/dependencies | 获取任务的所有前置任务 |
| GET | /api/tasks/{id}/dependents | 获取任务的所有被依赖者（谁依赖了我） |
| POST | /api/tasks/{id}/dependencies | 添加前置任务 |
| DELETE | /api/tasks/{id}/dependencies/{depends_on_id} | 删除前置任务 |

### 3.2 批量设置接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/tasks/batch-set-dependencies | 批量设置前置任务 |

请求体：
```json
{
  "task_ids": [3, 4, 5],           -- 要设置依赖的任务 IDs
  "depends_on_id": 1               -- 共同的前置任务 ID
}
```

响应：
```json
{
  "success": true,
  "updated": 3,
  "errors": []
}
```

### 3.3 获取可作为前置任务的任务

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/projects/{id}/available-dependencies?exclude={task_id} | 获取项目中可作为前置任务的任务列表（排除自身及后代） |

### 3.4 阻塞状态接口（扩展）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/tasks/{id}/block-status | 获取任务的阻塞状态 |

响应：
```json
{
  "task_id": 3,
  "is_blocked": true,
  "blocking_tasks": [
    {"id": 1, "title": "前置任务A", "status": "pending"}
  ],
  "all_dependencies_completed": false
}
```

## 4. 后端变更

### 4.1 models.py

```python
class TaskDependency(Base):
    __tablename__ = "task_dependencies"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"))
    depends_on_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"))
    dependency_type = Column(Text, default="requires")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    task = relationship("Task", foreign_keys=[task_id])
    depends_on = relationship("Task", foreign_keys=[depends_on_id])
```

### 4.2 阻塞检测逻辑更新

```python
def is_task_blocked(task_id: int) -> tuple[bool, list[dict]]:
    """检测任务是否被阻塞，返回 (是否阻塞, 阻塞任务列表)"""
    dependencies = db.query(TaskDependency).filter(
        TaskDependency.task_id == task_id
    ).all()
    
    blocking_tasks = []
    for dep in dependencies:
        dep_task = db.query(Task).get(dep.depends_on_id)
        if dep_task and dep_task.status != "completed":
            blocking_tasks.append({
                "id": dep_task.id,
                "title": dep_task.title,
                "status": dep_task.status
            })
    
    return len(blocking_tasks) > 0, blocking_tasks
```

### 4.3 循环引用检测

设置依赖时检测：
- A 依赖 B，B 依赖 A（直接循环）
- A 依赖 B，B 依赖 C，C 依赖 A（间接循环）

## 5. 前端变更

### 5.1 任务列表 - 批量选择

- 每行任务增加复选框
- 顶部显示已选数量
- 批量操作按钮："设置前置任务"

### 5.2 批量设置弹窗

```
┌─────────────────────────────────────┐
│ 批量设置前置任务                    │
├─────────────────────────────────────┤
│ 已选择: 3 个任务                    │
│                                     │
│ 选择前置任务:                       │
│ [下拉选择任务 ▼]                    │
│                                     │
│ [取消]              [确认设置]       │
└─────────────────────────────────────┘
```

### 5.3 任务详情页 - 依赖面板

```
┌─────────────────────────────────────────┐
│ 依赖关系                                │
├─────────────────────────────────────────┤
│ 🔗 我依赖的前置任务                     │
│   ├─ [ ] 任务A (pending) → 点击跳转    │
│   └─ [ ] 任务B (in_progress) → 点击跳转│
│                                         │
│ 🔗 依赖我的任务（被阻塞者）             │
│   ├─ [ ] 任务C (pending) - 等待任务A   │
│   └─ [ ] 任务D (pending) - 等待任务B   │
│                                         │
│ [+ 添加前置任务]                       │
└─────────────────────────────────────────┘
```

### 5.4 添加依赖弹窗

```
┌─────────────────────────────────────┐
│ 添加前置任务                         │
├─────────────────────────────────────┤
│ 选择前置任务:                       │
│ [搜索任务... ▼]                     │
│                                     │
│ 可选任务（同项目内）:                │
│ ○ 任务A                             │
│ ○ 任务B                             │
│ ○ 任务C                             │
│                                     │
│ [取消]              [确认添加]       │
└─────────────────────────────────────┘
```

### 5.5 任务卡片显示

- 显示前置任务数量 badge（如 "⏳ 2"）
- 被阻塞时显示灰色 + 阻塞提示

## 6. 交互流程

### 6.1 批量设置前置任务

```
1. 任务列表页，勾选多个任务
2. 点击"批量操作" → "设置前置任务"
3. 弹窗显示已选任务数量
4. 下拉选择共同的前置任务
5. 点击确认
6. 成功提示，刷新列表
```

### 6.2 查看依赖关系

```
1. 进入任务详情页
2. 滚动到"依赖关系"区块
3. 上半部分：显示所有前置任务（点击跳转）
4. 下半部分：显示所有依赖此任务的任务
5. 点击"+ 添加前置任务"可新增
```

### 6.3 删除依赖

```
1. 任务详情页 → 依赖面板
2. 鼠标悬停在前置任务上
3. 显示删除按钮（🗑）
4. 点击确认删除
```

## 7. 验收标准

### 功能验收

- [x] 能批量选择多个任务
- [x] 批量设置共同前置任务成功
- [x] 任务详情页显示"我依赖的前置任务"列表
- [x] 任务详情页显示"依赖我的任务"列表
- [x] 能添加单个前置任务
- [x] 能删除前置任务
- [x] 阻塞逻辑正确（任一前置未完成则阻塞）
- [x] 循环引用检测生效
- [x] 不同项目任务不能建立依赖

### 界面验收

- [x] 批量选择复选框正常显示
- [x] 批量操作按钮在有选中项时启用
- [x] 依赖面板双向显示完整
- [x] 点击任务可跳转

### 技术验收

- [x] 数据库迁移成功
- [x] API 接口正常
- [x] 前后端联调正常

## 8. 技术栈

- 后端：FastAPI + SQLite
- 前端：Vue 3 + TypeScript + Naive UI

## 9. 启动方式

```bash
# 后端
cd api && source venv/bin/activate && uvicorn main:app --reload

# 前端
cd web && npm run dev
```
