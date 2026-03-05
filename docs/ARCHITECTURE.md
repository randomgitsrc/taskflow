# TaskFlow 系统架构

> **版本**: 1.0  
> **更新**: 2026-03-05

## 1. 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        前端 (Vue 3)                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐    │
│  │TaskList │  │TaskTree │  │TaskDetail│  │ Statistics  │    │
│  └────┬────┘  └────┬────┘  └────┬────┘  └──────┬──────┘    │
│       │            │            │              │            │
│       └────────────┴────────────┴──────────────┘            │
│                          │                                  │
│                    axios / api/                             │
└──────────────────────────┼──────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │  REST API   │
                    │  (FastAPI)  │
                    └──────┬──────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐
│   models    │    │   crud      │    │  schemas    │
│  (SQLAlchemy)│    │ (数据库操作)│    │ (Pydantic) │
└──────┬──────┘    └──────┬──────┘    └─────────────┘
       │                   │
       │            ┌──────▼──────┐
       │            │   SQLite    │
       │            │ taskflow.db │
       │            └─────────────┘
       │
       └──────────────► (ORM)
```

## 2. 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 前端框架 | Vue 3 | 3.x |
| UI 组件 | Naive UI + Ant Design Vue | - |
| 状态管理 | Vue Composition API (ref/reactive) | - |
| HTTP 客户端 | axios | - |
| 后端框架 | FastAPI | 0.109+ |
| ORM | SQLAlchemy | 2.x |
| 数据库 | SQLite | - |
| 数据验证 | Pydantic | - |

## 3. 模块设计

### 3.1 后端模块

```
api/
├── main.py          # FastAPI 应用入口，路由定义
├── models.py        # SQLAlchemy 模型定义
├── schemas.py       # Pydantic 请求/响应模型
├── crud.py         # 数据库 CRUD 操作
└── database.py     # 数据库连接配置
```

**主要数据模型**:
- `Task` - 任务
- `Project` - 项目
- `Tag` - 标签
- `TaskLog` - 任务日志
- `Comment` - 评论
- `TaskDependency` - 任务依赖关系

### 3.2 前端模块

```
web/src/
├── views/           # 页面组件
│   ├── TaskList.vue     # 任务列表
│   ├── TaskTree.vue     # 任务树
│   ├── TaskDetail.vue   # 任务详情
│   └── Statistics.vue   # 统计页面
├── api/             # API 调用封装
│   ├── tasks.ts
│   └── projects.ts
├── components/      # 公共组件
├── router.ts       # 路由配置
└── App.vue         # 根组件
```

## 4. API 设计原则

| 原则 | 说明 |
|------|------|
| RESTful | 资源导向型 URL |
| 版本化 | 通过路径版本控制 `/api/v1/...` |
| 响应格式 | 统一 JSON 响应 `{code, data, message}` |
| 错误处理 | HTTP 状态码 + 业务错误码 |

## 5. 安全设计

- CORS 配置
- SQLAlchemy ORM 防止 SQL 注入
- Pydantic 数据验证

---

*最后更新: 2026-03-05*
