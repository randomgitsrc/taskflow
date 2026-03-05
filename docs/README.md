# TaskFlow 项目文档

> 项目管理工具，支持任务 CRUD、父子任务、依赖关系、标签、统计等功能。

## 📁 文档目录

| 文件 | 说明 | 版本 |
|------|------|------|
| [README.md](./README.md) | 项目概览和快速开始 | - |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | 系统架构设计 | v1.0 |
| [DATABASE.md](./DATABASE.md) | 数据库设计 | v1.0 |
| [API.md](./API.md) | 接口文档 | v1.0 |
| [CHANGELOG.md](./CHANGELOG.md) | 变更日志 | - |

## 📋 功能规格

| Phase | 内容 | 规格文件 |
|-------|------|----------|
| Phase 1 | 任务 CRUD、状态流转、树形结构、日志 | SPEC.md |
| Phase 2 | 父子任务、标签、优先级、统计 | SPEC.md |
| Phase 3 | 评论功能、进度百分比 | SPEC.md |
| Phase 4 | 父子任务阻塞逻辑 | SPEC.md |
| Phase 5 | 依赖关系完善 | SPEC-DEPENDENCY-ENHANCE.md |

## 🚀 快速开始

```bash
# 后端
cd api
source venv/bin/activate
uvicorn main:app --reload

# 前端
cd web
npm run dev
```

访问 http://localhost:5173

## 📂 项目结构

```
taskflow/
├── api/                 # 后端 (FastAPI)
│   ├── main.py         # 主应用
│   ├── models.py       # 数据模型
│   ├── schemas.py      # Pydantic 模型
│   ├── crud.py         # 数据库操作
│   └── database.py     # 数据库配置
├── web/                # 前端 (Vue 3 + TypeScript)
│   ├── src/
│   │   ├── views/     # 页面组件
│   │   ├── api/       # API 调用
│   │   └── components/# 公共组件
│   └── package.json
├── docs/               # 项目文档
└── SPEC*.md           # 功能规格说明书
```

## 🛠 技术栈

- **后端**: FastAPI + SQLite + SQLAlchemy
- **前端**: Vue 3 + TypeScript + Naive UI + Ant Design Vue
- **工具**: Claude Code (AI 辅助开发)

---

*最后更新: 2026-03-05*
