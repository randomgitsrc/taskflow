# 导出 Excel 功能 SPEC

## 概述
在任务列表页面增加「导出 Excel」功能

## 方案
前端导出，使用 xlsx 库（sheetjs）

## 实现

### 1. 安装依赖
```bash
cd ~/projects/personal/taskflow/web
npm install xlsx
```

### 2. UI 位置
在 TaskList.vue 顶部按钮区域，"刷新"按钮右侧增加"导出 Excel"按钮

### 3. 导出字段
| 列名 | 数据源 |
|------|--------|
| ID | task.id |
| 标题 | task.title |
| 项目 | project_id → projects 查找名称 |
| 优先级 | high→高, medium→中, low→低 |
| 状态 | 映射中文 |
| 进度 | progress + % |
| 负责人 | owner 或 "-" |
| 创建时间 | 格式化日期 |
| 父任务 | parent_id → tasks 查找标题 或 "-" |
| 标签 | tag_ids → tags 查找名称，逗号分隔 |

### 4. 文件名
`tasks_YYYYMMDD_HHMMSS.xlsx`

### 5. 导出范围
当前过滤后的任务（尊重用户筛选条件）
