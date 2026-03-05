"""FastAPI application for TaskFlow."""
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_, text

from database import get_db, engine, Base
from models import Task, TaskLog, TaskDependency
from schemas import (
    TaskCreate,
    TaskUpdate,
    TaskStatusUpdate,
    TaskResponse,
    TaskLogCreate,
    TaskLogResponse,
    TagCreate,
    TagUpdate,
    TagResponse,
    TaskProgressUpdate,
    CommentCreate,
    CommentResponse,
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    TaskDependencyCreate,
    BatchSetDependenciesRequest,
)
import crud

# Create tables
Base.metadata.create_all(bind=engine)

# Delete deprecated task_links table if exists (Phase 4)
# Add depends_on column if not exists (Dependency Phase 1)
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS task_links"))
    # Check if depends_on column exists
    result = conn.execute(text("PRAGMA table_info(tasks)"))
    columns = [row[1] for row in result]
    if "depends_on" not in columns:
        conn.execute(text("ALTER TABLE tasks ADD COLUMN depends_on TEXT"))
    conn.commit()

app = FastAPI(
    title="TaskFlow API",
    description="TaskFlow Web API",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Task endpoints
@app.get("/api/tasks", response_model=List[TaskResponse])
def get_tasks(
    q: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get all tasks with blocked info. Supports search via q parameter."""
    # Search query
    if q:
        # Try to convert search term to ID
        task_id = None
        try:
            task_id = int(q)
        except ValueError:
            pass

        # Build search conditions
        search_filter = or_(
            Task.title.contains(q),
            Task.description.contains(q)
        )
        if task_id is not None:
            search_filter = or_(
                Task.id == task_id,
                Task.title.contains(q),
                Task.description.contains(q)
            )

        tasks = db.query(Task).filter(search_filter).order_by(Task.created_at.desc()).all()
        result = []
        for task in tasks:
            result.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "priority": task.priority,
                "progress": task.progress,
                "parent_id": task.parent_id,
                "project_id": task.project_id,
                "owner": task.owner,
                "external_id": task.external_id,
                "external_type": task.external_type,
                "due_date": task.due_date,
                "started_at": task.started_at,
                "completed_at": task.completed_at,
                "depends_on": crud.get_task_depends_on(task),
                "created_at": task.created_at,
                "updated_at": task.updated_at,
                "is_blocked": crud.get_is_blocked(db, task.id),
                "parent_title": crud.get_parent_title(db, task.parent_id),
                "tag_ids": crud.get_task_tag_ids(db, task.id),
            })
        return result

    if status_filter:
        tasks = crud.get_tasks_by_status(db, status_filter)
        result = []
        for task in tasks:
            result.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "priority": task.priority,
                "progress": task.progress,
                "parent_id": task.parent_id,
                "project_id": task.project_id,
                "owner": task.owner,
                "external_id": task.external_id,
                "external_type": task.external_type,
                "due_date": task.due_date,
                "started_at": task.started_at,
                "completed_at": task.completed_at,
                "depends_on": crud.get_task_depends_on(task),
                "created_at": task.created_at,
                "updated_at": task.updated_at,
                "is_blocked": crud.get_is_blocked(db, task.id),
                "parent_title": crud.get_parent_title(db, task.parent_id),
                "tag_ids": crud.get_task_tag_ids(db, task.id),
            })
        return result
    return crud.get_tasks_with_blocked_info(db, skip=skip, limit=limit)


@app.get("/api/tasks/tree")
def get_task_tree(db: Session = Depends(get_db)):
    """Get task tree structure."""
    return crud.get_task_tree(db)


@app.post("/api/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task."""
    created_task = crud.create_task(db, task)
    # Manually build response to handle depends_on JSON parsing
    return {
        "id": created_task.id,
        "title": created_task.title,
        "description": created_task.description,
        "status": created_task.status,
        "priority": created_task.priority,
        "progress": created_task.progress,
        "parent_id": created_task.parent_id,
        "project_id": created_task.project_id,
        "owner": created_task.owner,
        "external_id": created_task.external_id,
        "external_type": created_task.external_type,
        "due_date": created_task.due_date,
        "started_at": created_task.started_at,
        "completed_at": created_task.completed_at,
        "depends_on": crud.get_task_depends_on(created_task),
        "created_at": created_task.created_at,
        "updated_at": created_task.updated_at,
        "is_blocked": crud.get_is_blocked(db, created_task.id),
        "parent_title": crud.get_parent_title(db, created_task.parent_id),
        "parent_status": crud.get_parent_status(db, created_task.parent_id),
        "tag_ids": crud.get_task_tag_ids(db, created_task.id),
    }


@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a task by ID."""
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Manually build response to handle depends_on JSON parsing
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "progress": task.progress,
        "parent_id": task.parent_id,
        "project_id": task.project_id,
        "owner": task.owner,
        "external_id": task.external_id,
        "external_type": task.external_type,
        "due_date": task.due_date,
        "started_at": task.started_at,
        "completed_at": task.completed_at,
        "depends_on": crud.get_task_depends_on(task),
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "is_blocked": crud.get_is_blocked(db, task.id),
        "parent_title": crud.get_parent_title(db, task.parent_id),
        "parent_status": crud.get_parent_status(db, task.parent_id),
        "tag_ids": crud.get_task_tag_ids(db, task.id),
    }


@app.put("/api/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    """Update a task."""
    updated_task = crud.update_task(db, task_id, task)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task


@app.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task."""
    if not crud.delete_task(db, task_id):
        raise HTTPException(status_code=404, detail="Task not found")


@app.patch("/api/tasks/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: int,
    status_update: TaskStatusUpdate,
    db: Session = Depends(get_db),
):
    """Update task status."""
    task = crud.update_task_status(db, task_id, status_update.status)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# Log endpoints
@app.get("/api/tasks/{task_id}/logs", response_model=List[TaskLogResponse])
def get_task_logs(task_id: int, db: Session = Depends(get_db)):
    """Get logs for a task."""
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.get_logs(db, task_id)


@app.post("/api/tasks/{task_id}/logs", response_model=TaskLogResponse, status_code=status.HTTP_201_CREATED)
def create_task_log(task_id: int, log: TaskLogCreate, db: Session = Depends(get_db)):
    """Create a log entry for a task."""
    db_log = crud.create_log(db, task_id, log.message)
    if not db_log:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_log


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


# Tag endpoints
@app.get("/api/tags", response_model=List[TagResponse])
def get_tags(db: Session = Depends(get_db)):
    """Get all tags."""
    return crud.get_tags(db)


@app.post("/api/tags", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    """Create a new tag."""
    return crud.create_tag(db, tag)


@app.put("/api/tags/{tag_id}", response_model=TagResponse)
def update_tag(tag_id: int, tag: TagUpdate, db: Session = Depends(get_db)):
    """Update a tag."""
    updated_tag = crud.update_tag(db, tag_id, tag)
    if not updated_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return updated_tag


@app.delete("/api/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """Delete a tag."""
    if not crud.delete_tag(db, tag_id):
        raise HTTPException(status_code=404, detail="Tag not found")


# Task-Tag endpoints
@app.get("/api/tasks/{task_id}/tags")
def get_task_tags(task_id: int, db: Session = Depends(get_db)):
    """Get all tags for a task."""
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.get_task_tags(db, task_id)


@app.post("/api/tasks/{task_id}/tags/{tag_id}", status_code=status.HTTP_201_CREATED)
def add_tag_to_task(task_id: int, tag_id: int, db: Session = Depends(get_db)):
    """Add a tag to a task."""
    result = crud.add_tag_to_task(db, task_id, tag_id)
    if not result:
        raise HTTPException(status_code=404, detail="Task or Tag not found")
    return {"status": "added"}


@app.delete("/api/tasks/{task_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_tag_from_task(task_id: int, tag_id: int, db: Session = Depends(get_db)):
    """Remove a tag from a task."""
    if not crud.remove_tag_from_task(db, task_id, tag_id):
        raise HTTPException(status_code=404, detail="Task tag not found")


# Phase 4: Available parent tasks endpoint
@app.get("/api/projects/{project_id}/available-parents")
def get_available_parent_tasks(
    project_id: int,
    exclude_task_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Get available tasks that can be set as parent for a new task."""
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    tasks = crud.get_available_parent_tasks(db, project_id, exclude_task_id)
    return [
        {
            "id": t.id,
            "title": t.title,
            "status": t.status,
            "priority": t.priority,
        }
        for t in tasks
    ]


# Stats endpoint
@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    """Get task statistics."""
    return crud.get_stats(db)


# Progress endpoint
@app.patch("/api/tasks/{task_id}/progress", response_model=TaskResponse)
def update_task_progress(
    task_id: int,
    progress_update: TaskProgressUpdate,
    db: Session = Depends(get_db),
):
    """Update task progress."""
    task = crud.update_task_progress(db, task_id, progress_update.progress)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# Comment endpoints
@app.get("/api/tasks/{task_id}/comments", response_model=List[CommentResponse])
def get_task_comments(task_id: int, db: Session = Depends(get_db)):
    """Get all comments for a task."""
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.get_comments(db, task_id)


@app.post("/api/tasks/{task_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_task_comment(task_id: int, comment: CommentCreate, db: Session = Depends(get_db)):
    """Create a comment for a task."""
    db_comment = crud.create_comment(db, task_id, comment)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_comment


@app.delete("/api/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    """Delete a comment."""
    if not crud.delete_comment(db, comment_id):
        raise HTTPException(status_code=404, detail="Comment not found")


# Project endpoints
@app.get("/api/projects", response_model=List[ProjectResponse])
def get_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get all projects."""
    return crud.get_projects(db, skip=skip, limit=limit)


@app.post("/api/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project."""
    return crud.create_project(db, project)


@app.get("/api/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a project by ID."""
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.put("/api/projects/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project: ProjectUpdate, db: Session = Depends(get_db)):
    """Update a project."""
    updated_project = crud.update_project(db, project_id, project)
    if not updated_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated_project


@app.delete("/api/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete a project."""
    # Check if project has tasks
    tasks = crud.get_tasks_by_project(db, project_id)
    if tasks:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete project: it has {len(tasks)} task(s). Please delete or move the tasks first."
        )
    if not crud.delete_project(db, project_id):
        raise HTTPException(status_code=404, detail="Project not found")


@app.get("/api/projects/{project_id}/tasks", response_model=List[TaskResponse])
def get_project_tasks(project_id: int, db: Session = Depends(get_db)):
    """Get all tasks for a project."""
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return crud.get_project_tasks(db, project_id)


# Phase 5: Task Dependencies endpoints

@app.get("/api/tasks/{task_id}/dependencies")
def get_task_dependencies(task_id: int, db: Session = Depends(get_db)):
    """Get all dependencies (前置任务) for a task."""
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    dependencies = crud.get_task_dependencies(db, task_id)
    result = []
    for dep in dependencies:
        dep_task = crud.get_task(db, dep.depends_on_id)
        if dep_task:
            result.append({
                "id": dep.id,
                "task_id": dep.task_id,
                "depends_on_id": dep.depends_on_id,
                "dependency_type": dep.dependency_type,
                "created_at": dep.created_at,
                "depends_on_title": dep_task.title,
                "depends_on_status": dep_task.status,
            })
    return result


@app.get("/api/tasks/{task_id}/dependents")
def get_task_dependents(task_id: int, db: Session = Depends(get_db)):
    """Get all dependent tasks (谁依赖了我)."""
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    dependents = crud.get_task_dependents(db, task_id)
    result = []
    for dep in dependents:
        dep_task = crud.get_task(db, dep.task_id)
        if dep_task:
            result.append({
                "id": dep.id,
                "task_id": dep.task_id,
                "depends_on_id": dep.depends_on_id,
                "dependency_type": dep.dependency_type,
                "created_at": dep.created_at,
                "task_title": dep_task.title,
                "task_status": dep_task.status,
            })
    return result


@app.post("/api/tasks/{task_id}/dependencies", status_code=status.HTTP_201_CREATED)
def add_task_dependency(task_id: int, dependency: TaskDependencyCreate, db: Session = Depends(get_db)):
    """Add a dependency to a task."""
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        result = crud.add_task_dependency(db, task_id, dependency.depends_on_id, dependency.dependency_type)
        if not result:
            raise HTTPException(status_code=404, detail="Dependency task not found")
        return {"status": "added", "id": result.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/tasks/{task_id}/dependencies/{depends_on_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_task_dependency(task_id: int, depends_on_id: int, db: Session = Depends(get_db)):
    """Remove a dependency from a task."""
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if not crud.remove_task_dependency(db, task_id, depends_on_id):
        raise HTTPException(status_code=404, detail="Dependency not found")


@app.post("/api/tasks/batch-set-dependencies")
def batch_set_dependencies(request: BatchSetDependenciesRequest, db: Session = Depends(get_db)):
    """Batch set dependencies for multiple tasks."""
    return crud.batch_set_dependencies(db, request.task_ids, request.depends_on_id)


@app.get("/api/projects/{project_id}/available-dependencies")
def get_available_dependencies(
    project_id: int,
    exclude_task_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Get available tasks that can be set as dependencies."""
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    tasks = crud.get_available_dependency_tasks(db, project_id, exclude_task_id)
    return [
        {
            "id": t.id,
            "title": t.title,
            "status": t.status,
            "priority": t.priority,
        }
        for t in tasks
    ]


@app.get("/api/tasks/{task_id}/block-status")
def get_block_status(task_id: int, db: Session = Depends(get_db)):
    """Get the blocking status of a task."""
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.get_block_status(db, task_id)
