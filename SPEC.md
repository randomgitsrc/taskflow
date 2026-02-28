# TaskFlow 技术规格说明书

> **版本**: 1.0.0  
> **更新**: 2026-02-28  
> **状态**: 开发中

## 1. 项目概述

- **项目名称**: TaskFlow
- **项目类型**: CLI 工具
- **核心功能**: 任务管理 CLI，支持任务树、状态机、任务关联
- **目标用户**: AI 助手（阿九）和用户（神龙）之间的协作任务管理

## 2. 技术栈

| 组件 | 技术 |
|------|------|
| 语言 | Python 3.8+ |
| CLI 框架 | Click |
| 数据库 | SQLite |
| 打包 | setuptools |

## 3. 功能列表

### 3.1 核心功能

| 功能 | 说明 |
|------|------|
| 任务创建 | 支持标题、描述、负责人、父子层级 |
| 任务状态 | 8 种状态：pending, in_progress, completed, stopped, paused, waiting, blocked, cancelled |
| 状态流转 | 状态机控制，允许有限状态转换 |
| 任务日志 | 记录任务变更历史 |
| 任务关联 | link/unlink 任务关系 |
| 任务树 | 树形结构展示任务层级 |

### 3.2 CLI 命令

| 命令 | 说明 |
|------|------|
| init | 初始化数据库 |
| add | 添加新任务 |
| list | 列出任务 |
| status | 查看任务详情 |
| done | 完成任务 |
| pause | 暂停任务 |
| resume | 恢复任务 |
| block | 阻塞任务 |
| cancel | 取消任务 |
| log | 添加日志 |
| logs | 查看日志 |
| tree | 树形视图 |
| link | 关联任务 |
| unlink | 解除关联 |

## 4. 数据模型

### 4.1 tasks 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| title | TEXT | 任务标题 |
| description | TEXT | 任务描述 |
| status | TEXT | 状态 |
| parent_id | INTEGER | 父任务 ID |
| owner | TEXT | 负责人 |
| external_id | TEXT | 外部关联 ID |
| external_type | TEXT | 外部类型 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 4.2 task_logs 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| task_id | INTEGER | 任务 ID |
| message | TEXT | 日志内容 |
| created_at | TIMESTAMP | 创建时间 |

### 4.3 task_links 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| task_id | INTEGER | 任务 ID |
| linked_task_id | INTEGER | 关联任务 ID |
| link_type | TEXT | 关联类型 |
| created_at | TIMESTAMP | 创建时间 |

## 5. 状态流转

```
pending → in_progress → completed
              ↓
          stopped
              ↓
         cancelled

pending → blocked → cancelled
pending → cancelled

in_progress → paused → in_progress
in_progress → waiting → in_progress
```

## 6. 使用示例

```bash
# 初始化
taskflow init

# 添加任务
taskflow add "完成代码"
taskflow add "写文档" --parent 1

# 查看
taskflow list
taskflow tree
taskflow status 1

# 操作
taskflow done 1
taskflow pause 1
taskflow resume 1
```

## 7. 后续迭代

- [ ] 支持 JSON/YAML 导入导出
- [ ] 支持任务标签
- [ ] 支持截止日期
- [ ] 支持任务优先级
