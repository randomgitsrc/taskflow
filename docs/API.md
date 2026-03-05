# TaskFlow API 接口文档

> **版本**: 1.0  
> **更新**: 2026-03-05

## 1. 接口概览

- **基础路径**: `/api`
- **认证**: 无（当前版本）
- **响应格式**: JSON

## 2. 任务接口

### 2.1 任务列表

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/tasks` | 获取所有任务 |
| GET | `/api/tasks/tree` | 获取任务树结构 |
| GET | `/api/tasks/{task_id}` | 获取任务详情 |
| POST | `/api/tasks` | 创建任务 |
| PUT | `/api/tasks/{task_id}` | 更新任务 |
| DELETE | `/api/tasks/{task_id}` | 删除任务 |
| PATCH | `/api/tasks/{task_id}/status` | 更新任务状态 |
| PATCH | `/api/tasks/{task_id}/progress` | 更新任务进度 |

### 2.2 任务日志

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/tasks/{task_id}/logs` | 获取任务日志列表 |
| POST | `/api/tasks/{task_id}/logs` | 添加任务日志 |

### 2.3 任务评论

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/tasks/{task_id}/comments` | 获取评论列表 |
| POST | `/api/tasks/{task_id}/comments` | 添加评论 |
| DELETE | `/api/comments/{comment_id}` | 删除评论 |

### 2.4 任务标签

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/tasks/{task_id}/tags` | 获取任务标签 |
| POST | `/api/tasks/{task_id}/tags/{tag_id}` | 添加标签 |
| DELETE | `/api/tasks/{task_id}/tags/{tag_id}` | 删除标签 |

### 2.5 任务依赖

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/tasks/{task_id}/dependencies` | 获取前置任务 |
| GET | `/api/tasks/{task_id}/dependents` | 获取被依赖者 |
| POST | `/api/tasks/{task_id}/dependencies` | 添加前置任务 |
| DELETE | `/api/tasks/{task_id}/dependencies/{depends_on_id}` | 删除前置任务 |
| POST | `/api/tasks/batch-set-dependencies` | 批量设置前置任务 |
| GET | `/api/tasks/{task_id}/block-status` | 获取阻塞状态 |

### 2.6 任务统计

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/stats` | 获取任务统计 |

## 3. 项目接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/projects` | 获取项目列表 |
| POST | `/api/projects` | 创建项目 |
| GET | `/api/projects/{project_id}` | 获取项目详情 |
| PUT | `/api/projects/{project_id}` | 更新项目 |
| DELETE | `/api/projects/{project_id}` | 删除项目 |
| GET | `/api/projects/{project_id}/tasks` | 获取项目任务 |
| GET | `/api/projects/{project_id}/available-parents` | 获取可选父任务 |
| GET | `/api/projects/{project_id}/available-dependencies` | 获取可选前置任务 |

## 4. 标签接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/tags` | 获取标签列表 |
| POST | `/api/tags` | 创建标签 |
| PUT | `/api/tags/{tag_id}` | 更新标签 |
| DELETE | `/api/tags/{tag_id}` | 删除标签 |

## 5. 通用接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |

---

*最后更新: 2026-03-05*
