# TaskFlow Web 版 Phase 3 规格说明书

> **版本**: 3.0.0
> **阶段**: Phase 3 - 评论功能 + 进度百分比 + 依赖可视化
> **更新**: 2026-03-03

## 1. 概述

Phase 3 在 Phase 2 基础上增加：
- 任务评论功能
- 进度百分比（0-100%）
- 依赖可视化（阻塞关系在任务树显示）

## 2. 概述（Phase 1-2）

Phase 1: 任务 CRUD、状态流转、树形结构、日志
Phase 2: 父子任务、任务关联、标签、优先级、统计页面

## 2. 技术变更

### 2.1 数据库

```sql
-- 新增 tags 表
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    color TEXT DEFAULT '#999999',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 新增 task_tags 关联表
CREATE TABLE IF NOT EXISTS task_tags (
    task_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (task_id, tag_id),
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- tasks 表新增字段
ALTER TABLE tasks ADD COLUMN priority TEXT DEFAULT 'medium';
-- priority: low, medium, high
```

### 2.2 目录结构

```
api/
├── main.py           # 新增标签/统计接口
├── models.py         # 新增 Tag 模型
├── schemas.py        # 新增 TagSchema
├── crud.py           # 新增 tag 相关方法
└── requirements.txt

web/
├── src/
│   ├── api/tasks.ts      # 新增 link/tag 接口
│   ├── views/
│   │   ├── TaskList.vue      # 标签/优先级筛选
│   │   ├── TaskTree.vue     # 父子层级展示
│   │   ├── TaskDetail.vue   # 关联/标签管理
│   │   └── Stats.vue        # 新增统计页面
│   └── components/
│       ├── TaskForm.vue      # 新增父任务选择
│       ├── TagManager.vue    # 新增标签管理组件
│       └── LinkManager.vue  # 新增关联管理组件
└── router.ts          # 新增统计路由
```

## 3. API 设计

### 3.1 标签接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/tags | 获取所有标签 |
| POST | /api/tags | 创建标签 |
| PUT | /api/tags/{id} | 更新标签 |
| DELETE | /api/tags/{id} | 删除标签 |

### 3.2 任务标签接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/tasks/{id}/tags | 获取任务的所有标签 |
| POST | /api/tasks/{id}/tags | 为任务添加标签 |
| DELETE | /api/tasks/{id}/tags/{tag_id} | 删除任务标签 |

### 3.3 任务关联接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/tasks/{id}/links | 获取任务的关联 |
| POST | /api/tasks/{id}/links | 添加关联 |
| DELETE | /api/tasks/{id}/links/{linked_id} | 删除关联 |

关联类型：`blocks`（阻塞）、`blocked_by`（被阻塞）、`depends_on`（依赖）、`related`（关联）

### 3.4 统计接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/stats | 获取统计数据 |

返回：
```json
{
  "total": 10,
  "pending": 3,
  "in_progress": 2,
  "completed": 5,
  "completed_rate": 0.5,
  "overdue": 1,
  "avg_duration_hours": 24.5
}
```

## 4. 前端页面

### 4.1 任务列表页增强

- 标签筛选下拉
- 优先级筛选（高/中/低）
- 任务卡片显示标签 badge
- 优先级 indicator

### 4.2 任务树增强

- 父子层级树形展示
- 拖拽调整父子关系（可选）
- 点击节点显示关联任务

### 4.3 任务详情页增强

- **标签管理**：添加/删除标签
- **关联管理**：添加前置/依赖/关联任务
- **优先级选择**：高/中/下拉选择

### 4.4 任务创建/编辑表单增强

- 父任务选择下拉
- 优先级选择
- 标签选择（多选）

### 4.5 统计页面

- 总任务数、进行中、已完成
- 完成率环形图
- 逾期任务列表
- 平均耗时

## 5. 交互流程

### 5.1 创建任务时设置父子

```
1. 点击"新建任务"
2. 弹出表单
3. "父任务"下拉选择已有任务
4. 提交创建
5. 任务树自动更新
```

### 5.2 添加任务关联

```
1. 进入任务详情页
2. 点击"关联管理"
3. 选择关联类型（前置/依赖/关联）
4. 选择关联的任务
5. 保存
```

### 5.3 打标签

```
1. 进入任务详情页
2. 点击"添加标签"
3. 选择已有标签或创建新标签
4. 标签显示在任务卡片上
```

## 6. 验收标准

### 功能验收

- [x] 能创建带父任务的任务
- [x] 任务树正确显示父子层级
- [x] 能添加/删除任务关联（前置/依赖/关联）
- [x] 能创建/编辑/删除标签
- [x] 能为任务打标签
- [x] 能设置任务优先级
- [x] 任务列表支持标签/优先级筛选
- [x] 统计页面显示正确数据

### 技术验收

- [x] 数据库迁移成功
- [x] API 接口正常
- [x] 前端页面正常加载
- [x] 前后端联调正常

## 7. 启动方式

与 Phase 1 相同：

```bash
# 后端
cd api && source venv/bin/activate && uvicorn main:app --reload

# 前端
cd web && npm run dev
```

## 8. Phase 2 变更总结 (2026-03-03)

### 数据库
- tasks 表新增 priority 字段
- 新增 tags 表
- 新增 task_tags 关联表
- 新增 task_links 关联表

### 后端 API
- 标签 CRUD: GET/POST/PUT/DELETE /api/tags
- 任务标签: GET/POST/DELETE /api/tasks/{id}/tags
- 任务关联: GET/POST/DELETE /api/tasks/{id}/links
- 统计: GET /api/stats

### 前端
- 任务列表：新增优先级、标签筛选，任务创建支持父任务/优先级/标签
- 任务详情：支持优先级修改、标签管理、关联管理
- 统计页面：环形图、状态分布、完成率等

## 9. 后续迭代

- 用户认证
- 逾期提醒
- 任务导入/导出

---

# Phase 3: 评论功能 + 进度百分比 + 依赖可视化

## 10. 数据库

```sql
-- tasks 表新增字段
ALTER TABLE tasks ADD COLUMN progress INTEGER DEFAULT 0;
-- progress: 0-100

-- comments 表（新增）
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    author TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);
```

## 11. API 设计

### 评论接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/tasks/{id}/comments | 获取任务评论 |
| POST | /api/tasks/{id}/comments | 添加评论 |
| DELETE | /api/comments/{id} | 删除评论 |

### 进度接口

| 方法 | 路径 | 说明 |
|------|------|------|
| PATCH | /api/tasks/{id}/progress | 更新进度 |

## 12. 前端

- 任务详情页：评论列表 + 添加评论 + 进度条
- 任务列表/树：显示进度百分比 + 阻塞关系可视化

## 13. 验收标准

- [x] 能添加/查看/删除评论
- [x] 进度显示 0-100%
- [x] 能修改进度
- [x] 阻塞关系在任务树可视化
---

# Phase 4: 父子任务状态约束

> **版本**: 4.0.0
> **更新**: 2026-03-04

## 1. 需求背景

原有关联功能（task_links）逻辑混乱，与 parent_id 功能重叠。本次重构：
- 删除 task_links 表
- 仅保留 parent_id 作为唯一父子关系
- 增加父子任务状态约束逻辑

## 2. 核心规则

### 2.1 父子任务约束

| 规则 | 说明 |
|------|------|
| 同项目 | 父子任务必须在同一项目内 |
| 唯一父节点 | 每个任务只能有一个父任务 |
| 根任务 | 无父任务的任务为"根任务" |

### 2.2 状态约束

| 父任务状态 | 子任务行为 |
|------------|------------|
| pending | 子任务"开始"按钮**禁用**，显示"等待父任务" |
| in_progress | 子任务"开始"按钮**可用** |
| completed | 子任务正常进行 |

### 2.3 状态联动

- **父任务完成** → 自动检查所有直接子任务，状态正常可用
- **子任务状态变更** → 仅影响下游（子任务的子任务），不影响上游

## 3. 数据库变更

```sql
-- 删除 task_links 表（不再使用）
DROP TABLE IF EXISTS task_links;

-- 可选：为 parent_id 添加项目约束（应用层实现）
-- parent_id 指向的任务必须与当前任务在同一 project_id 下
```

## 4. API 变更

### 4.1 任务列表返回新增字段

```json
{
  "id": 1,
  "title": "任务标题",
  "status": "pending",
  "parent_id": null,
  "project_id": 1,
  "is_blocked": true,  // 新增：是否被父任务阻塞
  "parent_title": null // 新增：父任务标题（前端展示用）
}
```

### 4.2 创建/更新任务接口

**创建任务**：
- 如果设置了 `parent_id`，验证：
  1. 父任务存在
  2. 父任务与当前任务在同一项目
  3. 不允许循环引用（A->B->A）

**更新任务**：
- 修改 `parent_id` 时同样验证上述条件
- 不允许将已完成任务设为子任务

### 4.3 获取可作为父任务的任务列表

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/projects/{id}/available-parents?exclude={task_id} | 获取项目中可作为父任务的任务列表（排除自身及后代） |

## 5. 前端变更

### 5.1 任务创建/编辑表单

- 父任务选择器：下拉列表，只显示**同项目内**的任务
- 显示"根任务"选项（清空父任务）
- 选中父任务后显示父任务标题预览

### 5.2 任务卡片/列表

- 显示父子层级缩进
- 被阻塞的任务：显示灰色 + "等待父任务" badge
- 父任务标题显示（如果有）

### 5.3 任务详情页

- 父子关系展示区：显示父任务（可点击跳转）
- 子任务列表：显示所有直接子任务
- 状态操作区：
  - 如果 `is_blocked=true`，"开始"按钮禁用 + 提示"等待父任务完成"

### 5.4 任务树

- 父子链清晰展示
- 阻塞状态可视化（灰显/锁图标）

## 6. 交互流程

### 6.1 创建子任务

```
1. 点击"新建任务"
2. 项目已选中
3. "父任务"下拉 → 显示同项目任务列表
4. 选择父任务（或留空=根任务）
5. 提交
6. 如果父任务未完成，新任务自动被阻塞
```

### 6.2 尝试开始被阻塞的任务

```
1. 点击"开始"按钮
2. 前端检查 is_blocked
3. 如果 is_blocked=true → 按钮禁用 + 提示"等待父任务完成"
4. 用户必须先完成父任务
```

### 6.3 完成父任务

```
1. 父任务状态改为"已完成"
2. 后端自动检查所有直接子任务的 is_blocked 状态
3. 前端刷新后，子任务"开始"按钮可用
```

## 7. 循环引用检测

```python
def validate_no_circular_reference(task_id, new_parent_id):
    """检测是否形成循环引用"""
    visited = set()
    current = new_parent_id
    
    while current:
        if current == task_id:
            raise ValueError("不能设置循环引用")
        if current in visited:
            raise ValueError("检测到循环引用")
        visited.add(current)
        # 获取当前节点的父节点
        current = get_parent_id(current)
    
    return True
```

## 8. 验收标准

### 功能验收

- [x] 能创建带父任务的子任务（同项目内）
- [x] 父任务未完成时，子任务"开始"按钮禁用
- [x] 父任务完成后，子任务自动解除阻塞
- [x] 切换父任务时检测循环引用
- [x] 不同项目的任务不能建立父子关系
- [x] 删除父任务时，子任务变为根任务（parent_id 设为 null）

### 界面验收

- [x] 父任务选择器只显示同项目任务
- [x] 被阻塞任务显示禁用状态和提示
- [x] 任务树清晰展示父子层级
- [x] 任务详情页显示父子关系

### 技术验收

- [x] task_links 表已删除
- [x] 数据库迁移正常
- [x] API 接口正常
- [x] 无循环引用 Bug

