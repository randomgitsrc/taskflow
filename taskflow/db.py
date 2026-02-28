"""Database models and operations for TaskFlow."""

import os
import sqlite3
from datetime import datetime
from enum import Enum
from __future__ import annotations
from typing import Optional, List, Dict, Any, Union

# Sentinel for distinguishing "not filtering" vs "filter by None"
class _UNSET:
    pass
UNSET = _UNSET()


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    STOPPED = "stopped"
    PAUSED = "paused"
    WAITING = "waiting"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


# Transitions allowed from each status
ALLOWED_TRANSITIONS = {
    TaskStatus.PENDING: [TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED, TaskStatus.BLOCKED],
    TaskStatus.IN_PROGRESS: [TaskStatus.COMPLETED, TaskStatus.STOPPED, TaskStatus.PAUSED, TaskStatus.WAITING, TaskStatus.BLOCKED],
    TaskStatus.STOPPED: [TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED],
    TaskStatus.PAUSED: [TaskStatus.IN_PROGRESS],
    TaskStatus.WAITING: [TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED],
    TaskStatus.BLOCKED: [TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED],
    TaskStatus.COMPLETED: [],
    TaskStatus.CANCELLED: [],
}


class Database:
    """SQLite database handler for TaskFlow."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.path.expanduser("~/.taskflow.db")
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self):
        """Connect to the database."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def init_db(self):
        """Initialize the database with required tables."""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                parent_id INTEGER,
                owner TEXT,
                external_id TEXT,
                external_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES tasks (id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                linked_task_id INTEGER NOT NULL,
                link_type TEXT DEFAULT 'related',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
                FOREIGN KEY (linked_task_id) REFERENCES tasks (id) ON DELETE CASCADE,
                UNIQUE(task_id, linked_task_id)
            )
        """)

        conn.commit()
        self.close()

    def _get_conn(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self.conn is None:
            return self.connect()
        return self.conn

    def create_task(
        self,
        title: str,
        description: Optional[str] = None,
        parent_id: Optional[int] = None,
        owner: Optional[str] = None,
        external_id: Optional[str] = None,
        external_type: Optional[str] = None
    ) -> int:
        """Create a new task and return its ID."""
        conn = self._get_conn()
        cursor = conn.cursor()
        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO tasks (title, description, status, parent_id, owner, external_id, external_type, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, description, TaskStatus.PENDING.value, parent_id, owner, external_id, external_type, now, now))

        conn.commit()
        return cursor.lastrowid

    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Get a task by ID."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def list_tasks(
        self,
        status: Optional[str] = None,
        owner: Optional[str] = None,
        parent_id: Optional[int] | _UNSET = UNSET
    ) -> List[Dict[str, Any]]:
        """List tasks with optional filters."""
        conn = self._get_conn()
        cursor = conn.cursor()

        query = "SELECT * FROM tasks WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status)
        if owner:
            query += " AND owner = ?"
            params.append(owner)
        if not isinstance(parent_id, _UNSET):
            if parent_id is None:
                query += " AND parent_id IS NULL"
            else:
                query += " AND parent_id = ?"
                params.append(parent_id)

        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def update_task_status(self, task_id: int, new_status: TaskStatus) -> bool:
        """Update task status."""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT status FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        if not row:
            return False

        current_status = TaskStatus(row["status"])
        if new_status not in ALLOWED_TRANSITIONS[current_status]:
            return False

        now = datetime.now().isoformat()
        cursor.execute(
            "UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?",
            (new_status.value, now, task_id)
        )
        conn.commit()
        return True

    def set_task_status(self, task_id: int, status: str) -> bool:
        """Set task status directly (for commands that don't check transitions)."""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
        if not cursor.fetchone():
            return False

        now = datetime.now().isoformat()
        cursor.execute(
            "UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?",
            (status, now, task_id)
        )
        conn.commit()
        return True

    def add_log(self, task_id: int, message: str) -> bool:
        """Add a log entry to a task."""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
        if not cursor.fetchone():
            return False

        cursor.execute(
            "INSERT INTO task_logs (task_id, message) VALUES (?, ?)",
            (task_id, message)
        )
        conn.commit()
        return True

    def get_logs(self, task_id: int) -> List[Dict[str, Any]]:
        """Get logs for a task."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM task_logs WHERE task_id = ? ORDER BY created_at DESC",
            (task_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def link_tasks(self, task_id: int, linked_task_id: int, link_type: str = "related") -> bool:
        """Link two tasks together."""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
        if not cursor.fetchone():
            return False

        cursor.execute("SELECT id FROM tasks WHERE id = ?", (linked_task_id,))
        if not cursor.fetchone():
            return False

        try:
            cursor.execute(
                "INSERT INTO task_links (task_id, linked_task_id, link_type) VALUES (?, ?, ?)",
                (task_id, linked_task_id, link_type)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def unlink_tasks(self, task_id: int, linked_task_id: int) -> bool:
        """Remove link between two tasks."""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM task_links WHERE task_id = ? AND linked_task_id = ?",
            (task_id, linked_task_id)
        )
        if cursor.rowcount == 0:
            cursor.execute(
                "DELETE FROM task_links WHERE task_id = ? AND linked_task_id = ?",
                (linked_task_id, task_id)
            )

        conn.commit()
        return cursor.rowcount > 0

    def get_linked_tasks(self, task_id: int) -> List[Dict[str, Any]]:
        """Get all tasks linked to a given task."""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT t.*, tl.link_type FROM tasks t
            JOIN task_links tl ON t.id = tl.linked_task_id
            WHERE tl.task_id = ?
            UNION
            SELECT t.*, tl.link_type FROM tasks t
            JOIN task_links tl ON t.id = tl.task_id
            WHERE tl.linked_task_id = ?
        """, (task_id, task_id))

        return [dict(row) for row in cursor.fetchall()]

    def get_task_tree(self, parent_id: Optional[int] | _UNSET = UNSET, depth: int = 0) -> List[Dict[str, Any]]:
        """Get task tree structure."""
        tasks = self.list_tasks(parent_id=parent_id)
        for task in tasks:
            task["children"] = self.get_task_tree(task["id"], depth + 1)
            task["depth"] = depth
        return tasks
