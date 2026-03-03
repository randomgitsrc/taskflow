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