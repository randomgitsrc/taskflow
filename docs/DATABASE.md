# TaskFlow 数据库设计

> **版本**: 1.0  
> **更新**: 2026-03-05

## 1. 数据库概览

- **数据库**: SQLite
- **文件**: `taskflow.db`
- **ORM**: SQLAlchemy

## 2. 数据表

### 2.1 projects (项目表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | TEXT | 项目名称 |
| description | TEXT | 项目描述 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 2.2 tasks (任务表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| title | TEXT | 任务标题 |
| description | TEXT | 任务描述 |
| status | TEXT | 状态 (pending/in_progress/completed/cancelled/stopped) |
| priority | TEXT | 优先级 (low/medium/high) |
| progress | INTEGER | 进度 (0-100) |
| parent_id | INTEGER | 父任务 ID (NULL 为顶级任务) |
| project_id | INTEGER | 所属项目 ID |
| owner | TEXT | 负责人 |
| external_id | TEXT | 外部系统 ID |
| external_type | TEXT | 外部系统类型 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 2.3 tags (标签表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | TEXT | 标签名称 |
| color | TEXT | 标签颜色 |
| created_at | TIMESTAMP | 创建时间 |

### 2.4 task_tags (任务-标签关联表)

| 字段 | 类型 | 说明 |
|------|------|------|
| task_id | INTEGER | 任务 ID |
| tag_id | INTEGER | 标签 ID |
| PRIMARY KEY | (task_id, tag_id) | 联合主键 |

### 2.5 task_logs (任务日志表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| task_id | INTEGER | 任务 ID |
| action | TEXT | 操作类型 |
| content | TEXT | 日志内容 |
| created_at | TIMESTAMP | 创建时间 |

### 2.6 comments (评论表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| task_id | INTEGER | 任务 ID |
| content | TEXT | 评论内容 |
| author | TEXT | 评论人 |
| created_at | TIMESTAMP | 创建时间 |

### 2.7 task_dependencies (任务依赖表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| task_id | INTEGER | 依赖方（被阻塞的任务） |
| depends_on_id | INTEGER | 被依赖方（前置任务） |
| dependency_type | TEXT | 依赖类型 (requires) |
| created_at | TIMESTAMP | 创建时间 |

## 3. ER 关系图

```
projects (1) ─────< (N) tasks
                              │
                              ├─< (N) task_logs
                              ├─< (N) comments
                              ├─< (N) task_tags >─ (1) tags
                              └─< (N) task_dependencies
                                               │
                                               └─< (1) tasks (自关联)
```

## 4. 索引

| 表名 | 索引字段 |
|------|----------|
| tasks | parent_id, project_id, status |
| task_logs | task_id |
| comments | task_id |
| task_tags | task_id, tag_id |
| task_dependencies | task_id, depends_on_id |

---

*最后更新: 2026-03-05*
