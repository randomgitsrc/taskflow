"""Pydantic schemas for TaskFlow API."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


# Project schemas
class ProjectBase(BaseModel):
    """Base project schema."""
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class ProjectResponse(ProjectBase):
    """Schema for project response."""
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Base schemas
class TaskBase(BaseModel):
    """Base task schema."""
    title: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    project_id: Optional[int] = None
    priority: Optional[str] = "medium"
    progress: Optional[int] = 0
    owner: Optional[str] = None
    external_id: Optional[str] = None
    external_type: Optional[str] = None
    due_date: Optional[datetime] = None
    depends_on: Optional[List[int]] = []  # Task dependency IDs


class TaskCreate(TaskBase):
    """Schema for creating a task."""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    project_id: Optional[int] = None
    priority: Optional[str] = None
    progress: Optional[int] = None
    owner: Optional[str] = None
    external_id: Optional[str] = None
    external_type: Optional[str] = None
    due_date: Optional[datetime] = None
    depends_on: Optional[List[int]] = None


class TaskStatusUpdate(BaseModel):
    """Schema for updating task status."""
    status: str


class TaskResponse(TaskBase):
    """Schema for task response."""
    id: int
    status: str
    progress: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    is_blocked: bool = False  # Phase 4: Whether task is blocked by parent
    parent_title: Optional[str] = None  # Phase 4: Parent task title for display
    parent_status: Optional[str] = None  # Phase 4: Parent task status for display
    tag_ids: List[int] = []  # List of tag IDs associated with this task

    model_config = ConfigDict(from_attributes=True)


class TaskWithChildren(TaskResponse):
    """Schema for task with children (tree view)."""
    children: List["TaskWithChildren"] = []


# Log schemas
class TaskLogBase(BaseModel):
    """Base log schema."""
    message: str


class TaskLogCreate(TaskLogBase):
    """Schema for creating a log."""
    pass


class TaskLogResponse(TaskLogBase):
    """Schema for log response."""
    id: int
    task_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Update forward ref
TaskWithChildren.model_rebuild()


# Tag schemas
class TagBase(BaseModel):
    """Base tag schema."""
    name: str
    color: str = "#999999"


class TagCreate(TagBase):
    """Schema for creating a tag."""
    pass


class TagUpdate(BaseModel):
    """Schema for updating a tag."""
    name: Optional[str] = None
    color: Optional[str] = None


class TagResponse(TagBase):
    """Schema for tag response."""
    id: int

    model_config = ConfigDict(from_attributes=True)


# Task-Tag schemas
class TaskTagResponse(BaseModel):
    """Schema for task-tag response."""
    task_id: int
    tag_id: int
    tag: TagResponse

    model_config = ConfigDict(from_attributes=True)


# Progress update schema
class TaskProgressUpdate(BaseModel):
    """Schema for updating task progress."""
    progress: int


# Comment schemas
class CommentBase(BaseModel):
    """Base comment schema."""
    author: str
    content: str


class CommentCreate(CommentBase):
    """Schema for creating a comment."""
    pass


class CommentResponse(CommentBase):
    """Schema for comment response."""
    id: int
    task_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
