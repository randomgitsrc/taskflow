# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TaskFlow is a task management application with three components:
- **CLI** (`taskflow/`): Python Click-based command-line tool
- **Web API** (`api/`): FastAPI backend with SQLAlchemy ORM + SQLite
- **Web Frontend** (`web/`): Vue 3 + TypeScript + Vite + Naive UI

## Common Commands

### Backend (API)
```bash
cd api
source venv/bin/activate
uvicorn main:app --reload
```
API runs at http://localhost:8000

### Frontend (Web)
```bash
cd web
npm install
npm run dev
```
Frontend runs at http://localhost:5173, proxies `/api` to localhost:8000

### CLI Installation
```bash
pip install -e .
taskflow --help
```

## Architecture

### Backend Structure (`api/`)
- `main.py`: FastAPI routes and endpoints
- `models.py`: SQLAlchemy ORM models (Task, Project, Tag, Comment, TaskLog)
- `schemas.py`: Pydantic request/response schemas
- `crud.py`: Database operations layer
- `database.py`: SQLAlchemy engine and session setup

**Key Models**:
- Task: Supports parent-child relationships, status (pending/in_progress/completed), priority, progress (0-100)
- Phase 4 feature: Parent-child status blocking - child tasks are blocked when parent is pending
- Project: Tasks belong to projects; parent/child tasks must be in same project

### Frontend Structure (`web/`)
- `src/api/tasks.ts`: Centralized API client - **all API calls go through here**
- `src/views/`: Page components (TaskList, TaskTree, TaskDetail, Stats, Projects)
- `src/router.ts`: Vue Router configuration
- `vite.config.ts`: Proxy `/api` → `http://localhost:8000`

**Development Rules** (from `.claude/rules/project.md`):
- Use Composition API (`<script setup lang="ts">`)
- All API calls go through `api/tasks.ts` - **never use fetch directly in components**

### API Client Pattern (`web/src/api/tasks.ts`)
```typescript
import api from './tasks'
// Use: api.getTasks(), api.createTask(data), etc.
```

## Key Features

### Phase 4: Parent-Child Task Constraints
- Child tasks are blocked (`is_blocked=true`) when parent status is `pending`
- Parent and child must belong to same project
- Circular reference detection when setting parent
- Endpoint: `GET /api/projects/{id}/available-parents` for parent selection UI

### Database Schema (SQLite)
Core tables: `tasks`, `projects`, `tags`, `task_tags`, `comments`, `task_logs`
Task statuses: `pending`, `in_progress`, `completed`
Task priorities: `low`, `medium`, `high`

## Testing

No automated test suite exists. Manual testing required:
1. Start backend: `cd api && uvicorn main:app --reload`
2. Start frontend: `cd web && npm run dev`
3. Test features through UI

## File Locations

- API entry: `api/main.py`
- Frontend entry: `web/src/main.ts`
- CLI entry: `taskflow/cli.py`
- Project config: `pyproject.toml`
- Frontend config: `web/package.json`, `web/vite.config.ts`

---

@rules/project.md

@session.md

@lessons.md
