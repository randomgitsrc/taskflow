"""FastAPI application for TaskFlow."""
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import get_db, engine, Base
from models import Task, TaskLog
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
    TaskLinkCreate,
    TaskLinkResponse,
    TaskProgressUpdate,
    CommentCreate,
    CommentResponse,
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
)
import crud

# Create tables
Base.metadata.create_all(bind=engine)

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
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get all tasks."""
    if status_filter:
        return crud.get_tasks_by_status(db, status_filter)
    return crud.get_tasks(db, skip=skip, limit=limit)


@app.get("/api/tasks/tree")
def get_task_tree(db: Session = Depends(get_db)):
    """Get task tree structure."""
    return crud.get_task_tree(db)


@app.post("/api/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task."""
    return crud.create_task(db, task)


@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a task by ID."""
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


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


# Task Link endpoints
@app.get("/api/tasks/{task_id}/links")
def get_task_links(task_id: int, db: Session = Depends(get_db)):
    """Get all links for a task."""
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.get_task_links(db, task_id)


@app.post("/api/tasks/{task_id}/links", status_code=status.HTTP_201_CREATED)
def create_task_link(task_id: int, link: TaskLinkCreate, db: Session = Depends(get_db)):
    """Create a link between tasks."""
    result = crud.create_task_link(db, task_id, link)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return result


@app.delete("/api/tasks/{task_id}/links/{linked_task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_link(task_id: int, linked_task_id: int, db: Session = Depends(get_db)):
    """Delete a link between tasks."""
    if not crud.delete_task_link(db, task_id, linked_task_id):
        raise HTTPException(status_code=404, detail="Task link not found")


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
    if not crud.delete_project(db, project_id):
        raise HTTPException(status_code=404, detail="Project not found")


@app.get("/api/projects/{project_id}/tasks", response_model=List[TaskResponse])
def get_project_tasks(project_id: int, db: Session = Depends(get_db)):
    """Get all tasks for a project."""
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return crud.get_project_tasks(db, project_id)
