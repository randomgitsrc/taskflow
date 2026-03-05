"""CRUD operations for TaskFlow."""
import json
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from models import Task, TaskLog, Tag, TaskTag, Comment, Project, TaskDependency
from schemas import TaskCreate, TaskUpdate, TagCreate, TagUpdate, CommentCreate, ProjectCreate, ProjectUpdate


# Dependency helpers
def get_task_depends_on(task: Task) -> Optional[List[int]]:
    """Parse JSON depends_on field to list of task IDs."""
    if not task.depends_on:
        return None
    try:
        return json.loads(task.depends_on)
    except json.JSONDecodeError:
        return None


def set_task_depends_on(task: Task, depends_on: Optional[List[int]]) -> None:
    """Set depends_on field as JSON string."""
    if depends_on is None or len(depends_on) == 0:
        task.depends_on = None
    else:
        task.depends_on = json.dumps(depends_on)


def get_tasks_by_dependency(db: Session, task_id: int) -> List[Task]:
    """Get all tasks that depend on the given task ID."""
    tasks = db.query(Task).all()
    result = []
    for task in tasks:
        depends_on = get_task_depends_on(task)
        if task_id in depends_on:
            result.append(task)
    return result


def check_dependencies_completed(db: Session, task: Task) -> bool:
    """Check if all dependencies of a task are completed."""
    depends_on = get_task_depends_on(task)
    if not depends_on:
        return True
    for dep_id in depends_on:
        dep_task = get_task(db, dep_id)
        if not dep_task or dep_task.status != "completed":
            return False
    return True


# Project CRUD
def get_project(db: Session, project_id: int) -> Optional[Project]:
    """Get a project by ID."""
    return db.query(Project).filter(Project.id == project_id).first()


def get_projects(db: Session, skip: int = 0, limit: int = 100) -> List[Project]:
    """Get all projects."""
    return db.query(Project).order_by(Project.created_at.desc()).offset(skip).limit(limit).all()


def get_project_by_name(db: Session, name: str) -> Optional[Project]:
    """Get a project by name."""
    return db.query(Project).filter(Project.name == name).first()


def create_project(db: Session, project: ProjectCreate) -> Project:
    """Create a new project."""
    db_project = Project(
        name=project.name,
        description=project.description,
        status="active",
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def update_project(db: Session, project_id: int, project: ProjectUpdate) -> Optional[Project]:
    """Update a project."""
    db_project = get_project(db, project_id)
    if not db_project:
        return None
    
    update_data = project.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    db_project.updated_at = datetime.now()
    db.commit()
    db.refresh(db_project)
    return db_project


def delete_project(db: Session, project_id: int) -> bool:
    """Delete a project."""
    db_project = get_project(db, project_id)
    if not db_project:
        return False
    db.delete(db_project)
    db.commit()
    return True


def get_project_tasks(db: Session, project_id: int) -> List[Task]:
    """Get all tasks for a project."""
    return db.query(Task).filter(Task.project_id == project_id).order_by(Task.created_at.desc()).all()


# Task CRUD
def get_task(db: Session, task_id: int) -> Optional[Task]:
    """Get a task by ID."""
    return db.query(Task).filter(Task.id == task_id).first()


def get_tasks(db: Session, skip: int = 0, limit: int = 100) -> List[Task]:
    """Get all tasks."""
    return db.query(Task).order_by(Task.created_at.desc()).offset(skip).limit(limit).all()


def get_tasks_with_blocked_info(db: Session, skip: int = 0, limit: int = 100) -> List[dict]:
    """Get all tasks with is_blocked and parent_title info."""
    tasks = db.query(Task).order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    result = []
    for task in tasks:
        task_dict = {
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
            "depends_on": get_task_depends_on(task),
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "is_blocked": get_is_blocked(db, task.id),
            "parent_title": get_parent_title(db, task.parent_id),
            "tag_ids": get_task_tag_ids(db, task.id),
        }
        result.append(task_dict)
    return result


def get_tasks_by_status(db: Session, status: str) -> List[Task]:
    """Get tasks by status."""
    return db.query(Task).filter(Task.status == status).order_by(Task.created_at.desc()).all()


def get_tasks_by_project(db: Session, project_id: int) -> List[Task]:
    """Get all tasks in a project."""
    return db.query(Task).filter(Task.project_id == project_id).order_by(Task.created_at.desc()).all()


def get_tasks_by_parent(db: Session, parent_id: Optional[int]) -> List[Task]:
    """Get tasks by parent ID."""
    if parent_id is None:
        return db.query(Task).filter(Task.parent_id == None).order_by(Task.created_at.desc()).all()
    return db.query(Task).filter(Task.parent_id == parent_id).order_by(Task.created_at.desc()).all()


def create_task(db: Session, task: TaskCreate) -> Task:
    """Create a new task with parent validation."""
    # Validate parent task if specified
    if task.parent_id:
        is_valid, error_msg = validate_parent_task(db, None, task.parent_id, task.project_id)
        if not is_valid:
            raise ValueError(error_msg)

    db_task = Task(
        title=task.title,
        description=task.description,
        parent_id=task.parent_id,
        project_id=task.project_id,
        priority=task.priority,
        owner=task.owner,
        external_id=task.external_id,
        external_type=task.external_type,
        due_date=task.due_date,
        status="pending",
    )

    # Set depends_on if provided
    if task.depends_on is not None:
        set_task_depends_on(db_task, task.depends_on)
        # Check if should be blocked
        if task.depends_on and not check_dependencies_completed(db, db_task):
            db_task.status = "blocked"

    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: int, task: TaskUpdate) -> Optional[Task]:
    """Update a task with parent validation."""
    db_task = get_task(db, task_id)
    if not db_task:
        return None

    # Validate parent_id if being updated
    if task.parent_id is not None and task.parent_id != db_task.parent_id:
        # Use the new parent_id and the existing or new project_id
        project_id = task.project_id if task.project_id is not None else db_task.project_id
        is_valid, error_msg = validate_parent_task(db, task_id, task.parent_id, project_id)
        if not is_valid:
            raise ValueError(error_msg)

    update_data = task.model_dump(exclude_unset=True)

    # Handle depends_on separately
    if "depends_on" in update_data:
        depends_on = update_data.pop("depends_on")
        set_task_depends_on(db_task, depends_on)
        # Check if should be blocked
        if depends_on and not check_dependencies_completed(db, db_task):
            db_task.status = "blocked"
        elif db_task.status == "blocked" and check_dependencies_completed(db, db_task):
            # Auto-unblock if dependencies are now completed
            db_task.status = "pending"

    for field, value in update_data.items():
        setattr(db_task, field, value)

    db_task.updated_at = datetime.now()
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int) -> bool:
    """Delete a task."""
    db_task = get_task(db, task_id)
    if not db_task:
        return False
    db.delete(db_task)
    db.commit()
    return True


def update_task_status(db: Session, task_id: int, status: str) -> Optional[Task]:
    """Update task status."""
    db_task = get_task(db, task_id)
    if not db_task:
        return None

    db_task.status = status
    db_task.updated_at = datetime.now()

    # Handle timestamps based on status
    if status == "in_progress" and not db_task.started_at:
        db_task.started_at = datetime.now()
    elif status == "completed":
        db_task.completed_at = datetime.now()
        # Check for tasks that depend on this one and unblock them
        unblock_dependent_tasks(db, task_id)

    db.commit()
    db.refresh(db_task)
    return db_task


def unblock_dependent_tasks(db: Session, completed_task_id: int) -> None:
    """When a task is completed, unblock tasks that depend on it."""
    dependent_tasks = get_tasks_by_dependency(db, completed_task_id)
    for task in dependent_tasks:
        if task.status == "blocked":
            # Check if all dependencies are now completed
            if check_dependencies_completed(db, task):
                task.status = "pending"
                db.add(task)
                # Create log entry
                create_log(db, task.id, f"前置任务 #{completed_task_id} 已完成，任务自动解除阻塞")
    db.commit()


def get_task_tree(db: Session, parent_id: Optional[int] = None) -> List[Task]:
    """Get task tree structure."""
    if parent_id is None:
        tasks = db.query(Task).filter(Task.parent_id == None).order_by(Task.created_at.desc()).all()
    else:
        tasks = db.query(Task).filter(Task.parent_id == parent_id).order_by(Task.created_at.desc()).all()

    result = []
    for task in tasks:
        # Get is_blocked status
        is_blocked = get_is_blocked(db, task.id)
        parent_title = get_parent_title(db, task.parent_id)

        task_dict = {
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
            "depends_on": get_task_depends_on(task),
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "is_blocked": is_blocked,
            "parent_title": parent_title,
            "children": get_task_tree(db, task.id)
        }
        result.append(task_dict)

    return result


# Log CRUD
def get_logs(db: Session, task_id: int) -> List[TaskLog]:
    """Get logs for a task."""
    return db.query(TaskLog).filter(TaskLog.task_id == task_id).order_by(TaskLog.created_at.desc()).all()


def create_log(db: Session, task_id: int, message: str) -> Optional[TaskLog]:
    """Create a log entry for a task."""
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    
    db_log = TaskLog(task_id=task_id, message=message)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


# Tag CRUD
def get_tags(db: Session) -> List[Tag]:
    """Get all tags."""
    return db.query(Tag).order_by(Tag.name).all()


def get_tag(db: Session, tag_id: int) -> Optional[Tag]:
    """Get a tag by ID."""
    return db.query(Tag).filter(Tag.id == tag_id).first()


def create_tag(db: Session, tag: TagCreate) -> Tag:
    """Create a new tag."""
    db_tag = Tag(name=tag.name, color=tag.color)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


def update_tag(db: Session, tag_id: int, tag: TagUpdate) -> Optional[Tag]:
    """Update a tag."""
    db_tag = get_tag(db, tag_id)
    if not db_tag:
        return None
    
    update_data = tag.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_tag, field, value)
    
    db.commit()
    db.refresh(db_tag)
    return db_tag


def delete_tag(db: Session, tag_id: int) -> bool:
    """Delete a tag."""
    db_tag = get_tag(db, tag_id)
    if not db_tag:
        return False
    db.delete(db_tag)
    db.commit()
    return True


# Task-Tag CRUD
def get_task_tags(db: Session, task_id: int) -> List[Tag]:
    """Get all tags for a task (returns Tag objects with name and color)."""
    return db.query(Tag).join(TaskTag, Tag.id == TaskTag.tag_id).filter(TaskTag.task_id == task_id).all()


def get_task_tag_ids(db: Session, task_id: int) -> List[int]:
    """Get all tag IDs for a task."""
    return [t.tag_id for t in db.query(TaskTag.tag_id).filter(TaskTag.task_id == task_id).all()]


def get_task_tag_names(db: Session, task_id: int) -> List[dict]:
    """Get tags with details for a task."""
    return db.query(TaskTag, Tag).join(Tag, TaskTag.tag_id == Tag.id).filter(TaskTag.task_id == task_id).all()


def add_tag_to_task(db: Session, task_id: int, tag_id: int) -> Optional[TaskTag]:
    """Add a tag to a task."""
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    
    db_tag = get_tag(db, tag_id)
    if not db_tag:
        return None
    
    # Check if already exists
    existing = db.query(TaskTag).filter(TaskTag.task_id == task_id, TaskTag.tag_id == tag_id).first()
    if existing:
        return existing
    
    db_task_tag = TaskTag(task_id=task_id, tag_id=tag_id)
    db.add(db_task_tag)
    db.commit()
    db.refresh(db_task_tag)
    return db_task_tag


def remove_tag_from_task(db: Session, task_id: int, tag_id: int) -> bool:
    """Remove a tag from a task."""
    db_task_tag = db.query(TaskTag).filter(TaskTag.task_id == task_id, TaskTag.tag_id == tag_id).first()
    if not db_task_tag:
        return False
    db.delete(db_task_tag)
    db.commit()
    return True


# Stats
def get_stats(db: Session) -> dict:
    """Get task statistics."""
    total = db.query(Task).count()
    pending = db.query(Task).filter(Task.status == "pending").count()
    in_progress = db.query(Task).filter(Task.status == "in_progress").count()
    completed = db.query(Task).filter(Task.status == "completed").count()
    
    completed_rate = completed / total if total > 0 else 0
    
    # Overdue tasks
    now = datetime.now()
    overdue = db.query(Task).filter(
        Task.due_date < now,
        Task.status != "completed"
    ).count()
    
    # Average duration (for completed tasks)
    completed_tasks = db.query(Task).filter(
        Task.status == "completed",
        Task.started_at.isnot(None),
        Task.completed_at.isnot(None)
    ).all()
    
    total_hours = 0
    count = 0
    for task in completed_tasks:
        if task.started_at and task.completed_at:
            duration = (task.completed_at - task.started_at).total_seconds() / 3600
            total_hours += duration
            count += 1
    
    avg_duration_hours = total_hours / count if count > 0 else 0
    
    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "completed": completed,
        "completed_rate": round(completed_rate, 2),
        "overdue": overdue,
        "avg_duration_hours": round(avg_duration_hours, 1)
    }


# Progress update
def update_task_progress(db: Session, task_id: int, progress: int) -> Optional[Task]:
    """Update task progress (0-100)."""
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    
    # Clamp progress to 0-100
    db_task.progress = max(0, min(100, progress))
    db_task.updated_at = datetime.now()
    db.commit()
    db.refresh(db_task)
    return db_task


# Comment CRUD
def get_comments(db: Session, task_id: int) -> List[Comment]:
    """Get all comments for a task."""
    return db.query(Comment).filter(Comment.task_id == task_id).order_by(Comment.created_at.desc()).all()


def get_comment(db: Session, comment_id: int) -> Optional[Comment]:
    """Get a comment by ID."""
    return db.query(Comment).filter(Comment.id == comment_id).first()


def create_comment(db: Session, task_id: int, comment: CommentCreate) -> Optional[Comment]:
    """Create a comment for a task."""
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    
    db_comment = Comment(
        task_id=task_id,
        author=comment.author,
        content=comment.content
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def delete_comment(db: Session, comment_id: int) -> bool:
    """Delete a comment."""
    db_comment = get_comment(db, comment_id)
    if not db_comment:
        return False
    db.delete(db_comment)
    db.commit()
    return True


# Phase 4: Parent-child task validation and blocking logic

def validate_parent_task(db: Session, task_id: Optional[int], new_parent_id: Optional[int], project_id: Optional[int]) -> tuple[bool, str]:
    """
    Validate parent task selection.
    Returns (is_valid, error_message)
    """
    if new_parent_id is None:
        return True, ""

    # Get parent task
    parent_task = get_task(db, new_parent_id)
    if not parent_task:
        return False, "父任务不存在"

    # Check same project constraint
    if project_id is not None and parent_task.project_id != project_id:
        return False, "父任务必须在同一项目内"

    # Check if parent is completed (cannot set as parent if completed)
    if parent_task.status == "completed":
        return False, "已完成的任务不能作为父任务"

    # Check circular reference
    if task_id is not None:
        if new_parent_id == task_id:
            return False, "不能将任务设置为自己的父任务"

        # Check if task_id is an ancestor of new_parent_id (would create circular reference)
        visited = set()
        current = new_parent_id
        while current:
            if current == task_id:
                return False, "不能设置循环引用"
            if current in visited:
                return False, "检测到循环引用"
            visited.add(current)
            parent = get_task(db, current)
            current = parent.parent_id if parent else None

    return True, ""


def get_is_blocked(db: Session, task_id: int) -> bool:
    """
    Check if a task is blocked by its dependencies (前置任务).
    Task is blocked if:
    1. Has depends_on (前置任务)
    2. Any dependency is not completed
    """
    task = get_task(db, task_id)
    if not task:
        return False

    depends = get_task_depends_on(task)
    if not depends:
        return False

    # Check if any dependency is not completed
    for dep_id in depends:
        dep_task = get_task(db, dep_id)
        if dep_task and dep_task.status != "completed":
            return True

    return False


def get_parent_title(db: Session, parent_id: Optional[int]) -> Optional[str]:
    """Get parent task title."""
    if not parent_id:
        return None
    parent = get_task(db, parent_id)
    return parent.title if parent else None


def get_parent_status(db: Session, parent_id: Optional[int]) -> Optional[str]:
    """Get parent task status."""
    if not parent_id:
        return None
    parent = get_task(db, parent_id)
    return parent.status if parent else None


def get_available_parent_tasks(db: Session, project_id: int, exclude_task_id: Optional[int] = None) -> List[Task]:
    """
    Get available tasks that can be set as parent for a new task.
    Excludes the task itself and all its descendants.
    """
    # Get all tasks in the project
    tasks = db.query(Task).filter(Task.project_id == project_id).all()

    # If excluding a task, also exclude its descendants
    exclude_ids = set()
    if exclude_task_id:
        exclude_ids.add(exclude_task_id)
        # BFS to find all descendants
        queue = [exclude_task_id]
        while queue:
            current = queue.pop()
            children = db.query(Task).filter(Task.parent_id == current).all()
            for child in children:
                if child.id not in exclude_ids:
                    exclude_ids.add(child.id)
                    queue.append(child.id)

    # Filter out excluded tasks and completed tasks
    available = [t for t in tasks if t.id not in exclude_ids and t.status != "completed"]
    return available


# Phase 5: Task Dependencies CRUD

def get_task_dependencies(db: Session, task_id: int) -> List[TaskDependency]:
    """Get all dependencies (前置任务) for a task."""
    return db.query(TaskDependency).filter(TaskDependency.task_id == task_id).all()


def get_task_dependents(db: Session, task_id: int) -> List[TaskDependency]:
    """Get all dependent tasks (被依赖者 - tasks that depend on this task)."""
    return db.query(TaskDependency).filter(TaskDependency.depends_on_id == task_id).all()


def add_task_dependency(db: Session, task_id: int, depends_on_id: int, dependency_type: str = "requires") -> Optional[TaskDependency]:
    """Add a dependency to a task."""
    # Validate task exists
    task = get_task(db, task_id)
    if not task:
        return None

    # Validate depends_on task exists
    dep_task = get_task(db, depends_on_id)
    if not dep_task:
        return None

    # Check same project constraint
    if task.project_id and dep_task.project_id and task.project_id != dep_task.project_id:
        raise ValueError("只能设置同一项目内的任务作为前置任务")

    # Check circular reference
    if check_circular_dependency(db, task_id, depends_on_id):
        raise ValueError("检测到循环引用，不能设置依赖关系")

    # Check if dependency already exists
    existing = db.query(TaskDependency).filter(
        TaskDependency.task_id == task_id,
        TaskDependency.depends_on_id == depends_on_id
    ).first()
    if existing:
        return existing

    db_dependency = TaskDependency(
        task_id=task_id,
        depends_on_id=depends_on_id,
        dependency_type=dependency_type
    )
    db.add(db_dependency)
    db.commit()
    db.refresh(db_dependency)

    # Update task blocking status
    update_task_blocking_status(db, task_id)

    return db_dependency


def remove_task_dependency(db: Session, task_id: int, depends_on_id: int) -> bool:
    """Remove a dependency from a task."""
    db_dependency = db.query(TaskDependency).filter(
        TaskDependency.task_id == task_id,
        TaskDependency.depends_on_id == depends_on_id
    ).first()

    if not db_dependency:
        return False

    db.delete(db_dependency)
    db.commit()

    # Update task blocking status
    update_task_blocking_status(db, task_id)

    return True


def check_circular_dependency(db: Session, task_id: int, depends_on_id: int) -> bool:
    """
    Check if adding a dependency would create a circular reference.
    A -> B means A depends on B.
    If B already depends on A (directly or indirectly), it's a circular reference.
    """
    # BFS/DFS to check if task_id is reachable from depends_on_id
    visited = set()
    queue = [depends_on_id]

    while queue:
        current = queue.pop(0)
        if current == task_id:
            return True
        if current in visited:
            continue
        visited.add(current)

        # Get all tasks that current depends on
        deps = db.query(TaskDependency).filter(TaskDependency.task_id == current).all()
        for dep in deps:
            if dep.depends_on_id not in visited:
                queue.append(dep.depends_on_id)

    return False


def update_task_blocking_status(db: Session, task_id: int) -> None:
    """Update task status based on dependencies. If any dependency is not completed, task becomes blocked."""
    task = get_task(db, task_id)
    if not task:
        return

    dependencies = get_task_dependencies(db, task_id)
    if not dependencies:
        # No dependencies - task should not be blocked
        if task.status == "blocked":
            task.status = "pending"
            db.commit()
        return

    # Check if any dependency is not completed (AND relationship)
    blocking = False
    for dep in dependencies:
        dep_task = get_task(db, dep.depends_on_id)
        if dep_task and dep_task.status != "completed":
            blocking = True
            break

    if blocking and task.status != "blocked":
        task.status = "blocked"
        db.commit()
    elif not blocking and task.status == "blocked":
        task.status = "pending"
        db.commit()


def get_block_status(db: Session, task_id: int) -> dict:
    """Get the blocking status of a task."""
    task = get_task(db, task_id)
    if not task:
        return {"task_id": task_id, "is_blocked": False, "blocking_tasks": [], "all_dependencies_completed": True}

    dependencies = get_task_dependencies(db, task_id)
    blocking_tasks = []
    all_completed = True

    for dep in dependencies:
        dep_task = get_task(db, dep.depends_on_id)
        if dep_task:
            if dep_task.status != "completed":
                all_completed = False
                blocking_tasks.append({
                    "id": dep_task.id,
                    "title": dep_task.title,
                    "status": dep_task.status
                })

    return {
        "task_id": task_id,
        "is_blocked": len(blocking_tasks) > 0,
        "blocking_tasks": blocking_tasks,
        "all_dependencies_completed": all_completed
    }


def batch_set_dependencies(db: Session, task_ids: List[int], depends_on_id: int) -> dict:
    """
    Batch set dependencies for multiple tasks.
    Uses append mode - adds the dependency without removing existing ones.
    Returns dict with success, updated count, and errors.
    """
    errors = []
    updated = 0

    # Validate depends_on task
    dep_task = get_task(db, depends_on_id)
    if not dep_task:
        return {"success": False, "updated": 0, "errors": [f"前置任务 #{depends_on_id} 不存在"]}

    for task_id in task_ids:
        try:
            task = get_task(db, task_id)
            if not task:
                errors.append(f"任务 #{task_id} 不存在")
                continue

            # Check same project constraint
            if task.project_id and dep_task.project_id and task.project_id != dep_task.project_id:
                errors.append(f"任务 #{task_id} 和前置任务不在同一项目内")
                continue

            # Check circular dependency
            if check_circular_dependency(db, task_id, depends_on_id):
                errors.append(f"任务 #{task_id} 会形成循环引用")
                continue

            # Check if dependency already exists
            existing = db.query(TaskDependency).filter(
                TaskDependency.task_id == task_id,
                TaskDependency.depends_on_id == depends_on_id
            ).first()

            if not existing:
                db_dependency = TaskDependency(
                    task_id=task_id,
                    depends_on_id=depends_on_id,
                    dependency_type="requires"
                )
                db.add(db_dependency)
                updated += 1

            # Update blocking status
            update_task_blocking_status(db, task_id)

        except ValueError as e:
            errors.append(f"任务 #{task_id}: {str(e)}")
        except Exception as e:
            errors.append(f"任务 #{task_id}: {str(e)}")

    db.commit()
    return {
        "success": len(errors) == 0,
        "updated": updated,
        "errors": errors
    }


def get_available_dependency_tasks(db: Session, project_id: int, exclude_task_id: Optional[int] = None) -> List[Task]:
    """
    Get available tasks that can be set as dependencies for tasks in this project.
    Excludes the task itself and all its descendants (to avoid circular dependencies).
    """
    # Get all tasks in the project
    tasks = db.query(Task).filter(Task.project_id == project_id).all()

    # If excluding a task, also exclude its descendants
    exclude_ids = set()
    if exclude_task_id:
        exclude_ids.add(exclude_task_id)
        # BFS to find all descendants
        queue = [exclude_task_id]
        while queue:
            current = queue.pop()
            children = db.query(Task).filter(Task.parent_id == current).all()
            for child in children:
                if child.id not in exclude_ids:
                    exclude_ids.add(child.id)
                    queue.append(child.id)

    # Filter out excluded tasks
    available = [t for t in tasks if t.id not in exclude_ids]
    return available
