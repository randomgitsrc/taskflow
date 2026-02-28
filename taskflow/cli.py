"""CLI commands for TaskFlow."""

import click
from datetime import datetime
from typing import Optional

from .db import Database, TaskStatus


@click.group()
@click.version_option(version="0.1.0", prog_name="taskflow")
@click.option('--db-path', type=click.Path(), help='Path to the database file')
@click.pass_context
def cli(ctx: click.Context, db_path: Optional[str]):
    """TaskFlow - A simple task management CLI tool."""
    ctx.ensure_object(dict)
    ctx.obj['db'] = Database(db_path)


@cli.command()
@click.pass_context
def init(ctx: click.Context):
    """Initialize the database."""
    db = ctx.obj['db']
    db.init_db()
    click.echo(f"Database initialized at: {db.db_path}")


@cli.command()
@click.argument('title')
@click.option('--description', '-d', help='Task description')
@click.option('--parent', '-p', type=int, help='Parent task ID')
@click.option('--owner', '-o', help='Task owner')
@click.option('--external-id', help='External ID reference')
@click.option('--external-type', help='External type reference')
@click.pass_context
def add(ctx: click.Context, title: str, description: Optional[str], parent: Optional[int],
        owner: Optional[str], external_id: Optional[str], external_type: Optional[str]):
    """Add a new task."""
    db = ctx.obj['db']
    task_id = db.create_task(
        title=title,
        description=description,
        parent_id=parent,
        owner=owner,
        external_id=external_id,
        external_type=external_type
    )
    click.echo(f"Task created: #{task_id} - {title}")


@cli.command()
@click.option('--status', '-s', type=click.Choice([s.value for s in TaskStatus]), help='Filter by status')
@click.option('--owner', '-o', help='Filter by owner')
@click.option('--parent', '-p', type=int, help='Filter by parent task ID')
@click.pass_context
def list(ctx: click.Context, status: Optional[str], owner: Optional[str], parent: Optional[int]):
    """List tasks."""
    db = ctx.obj['db']
    tasks = db.list_tasks(status=status, owner=owner, parent_id=parent)

    if not tasks:
        click.echo("No tasks found.")
        return

    click.echo(f"{'ID':<6} {'Status':<12} {'Owner':<12} {'Title'}")
    click.echo("-" * 60)
    for task in tasks:
        status_display = task['status']
        owner_display = task['owner'] or '-'
        click.echo(f"#{task['id']:<5} {status_display:<12} {owner_display:<12} {task['title']}")


@cli.command()
@click.argument('task_id', type=int)
@click.pass_context
def status(ctx: click.Context, task_id: int):
    """Show detailed status of a task."""
    db = ctx.obj['db']
    task = db.get_task(task_id)

    if not task:
        click.echo(f"Task #{task_id} not found.", err=True)
        raise click.Exit(1)

    click.echo(f"Task #{task['id']}: {task['title']}")
    click.echo(f"  Status: {task['status']}")
    if task['description']:
        click.echo(f"  Description: {task['description']}")
    if task['owner']:
        click.echo(f"  Owner: {task['owner']}")
    if task['parent_id']:
        click.echo(f"  Parent: #{task['parent_id']}")
    if task['external_id']:
        click.echo(f"  External ID: {task['external_id']} ({task['external_type'] or 'unknown'})")
    click.echo(f"  Created: {task['created_at']}")
    click.echo(f"  Updated: {task['updated_at']}")


@cli.command()
@click.argument('task_id', type=int)
@click.pass_context
def done(ctx: click.Context, task_id: int):
    """Mark a task as completed."""
    db = ctx.obj['db']
    if db.update_task_status(task_id, TaskStatus.COMPLETED):
        click.echo(f"Task #{task_id} marked as completed.")
    else:
        task = db.get_task(task_id)
        if not task:
            click.echo(f"Task #{task_id} not found.", err=True)
        else:
            click.echo(f"Cannot complete task #{task_id} from status '{task['status']}'.", err=True)
        raise click.Exit(1)


@cli.command()
@click.argument('task_id', type=int)
@click.pass_context
def pause(ctx: click.Context, task_id: int):
    """Pause a task."""
    db = ctx.obj['db']
    if db.update_task_status(task_id, TaskStatus.PAUSED):
        click.echo(f"Task #{task_id} paused.")
    else:
        task = db.get_task(task_id)
        if not task:
            click.echo(f"Task #{task_id} not found.", err=True)
        else:
            click.echo(f"Cannot pause task #{task_id} from status '{task['status']}'.", err=True)
        raise click.Exit(1)


@cli.command()
@click.argument('task_id', type=int)
@click.pass_context
def resume(ctx: click.Context, task_id: int):
    """Resume a paused task."""
    db = ctx.obj['db']
    if db.update_task_status(task_id, TaskStatus.IN_PROGRESS):
        click.echo(f"Task #{task_id} resumed.")
    else:
        task = db.get_task(task_id)
        if not task:
            click.echo(f"Task #{task_id} not found.", err=True)
        else:
            click.echo(f"Cannot resume task #{task_id} from status '{task['status']}'.", err=True)
        raise click.Exit(1)


@cli.command()
@click.argument('task_id', type=int)
@click.option('--blocked-by', '-b', type=int, help='Task ID that blocks this task')
@click.pass_context
def block(ctx: click.Context, task_id: int, blocked_by: Optional[int]):
    """Block a task or set what blocks it."""
    db = ctx.obj['db']

    if blocked_by:
        db.link_tasks(task_id, blocked_by, "blocks")
        click.echo(f"Task #{blocked_by} now blocks task #{task_id}.")

    if db.update_task_status(task_id, TaskStatus.BLOCKED):
        click.echo(f"Task #{task_id} blocked.")
    else:
        task = db.get_task(task_id)
        if not task:
            click.echo(f"Task #{task_id} not found.", err=True)
            raise click.Exit(1)


@cli.command()
@click.argument('task_id', type=int)
@click.pass_context
def cancel(ctx: click.Context, task_id: int):
    """Cancel a task."""
    db = ctx.obj['db']

    task = db.get_task(task_id)
    if not task:
        click.echo(f"Task #{task_id} not found.", err=True)
        raise click.Exit(1)

    current_status = TaskStatus(task['status'])
    if TaskStatus.CANCELLED in db.ALLOWED_TRANSITIONS.get(current_status, []):
        if db.update_task_status(task_id, TaskStatus.CANCELLED):
            click.echo(f"Task #{task_id} cancelled.")
        else:
            click.echo(f"Failed to cancel task #{task_id}.", err=True)
            raise click.Exit(1)
    else:
        if current_status == TaskStatus.CANCELLED:
            click.echo(f"Task #{task_id} is already cancelled.")
        else:
            db.set_task_status(task_id, TaskStatus.CANCELLED.value)
            click.echo(f"Task #{task_id} cancelled.")


@cli.command()
@click.argument('task_id', type=int)
@click.argument('message')
@click.pass_context
def log(ctx: click.Context, task_id: int, message: str):
    """Add a log entry to a task."""
    db = ctx.obj['db']
    if db.add_log(task_id, message):
        click.echo(f"Log added to task #{task_id}.")
    else:
        click.echo(f"Task #{task_id} not found.", err=True)
        raise click.Exit(1)


@cli.command()
@click.argument('task_id', type=int)
@click.pass_context
def logs(ctx: click.Context, task_id: int):
    """Show logs for a task."""
    db = ctx.obj['db']
    logs = db.get_logs(task_id)

    if not logs:
        click.echo("No logs found.")
        return

    click.echo(f"Logs for task #{task_id}:")
    for log in logs:
        timestamp = log['created_at']
        click.echo(f"  [{timestamp}] {log['message']}")


@cli.command()
@click.pass_context
def tree(ctx: click.Context):
    """Show task tree structure."""
    db = ctx.obj['db']
    trees = db.get_task_tree()

    def print_tree(tasks, indent=0):
        for task in tasks:
            prefix = "  " * indent
            status = task['status']
            click.echo(f"{prefix}[{status}] #{task['id']} {task['title']}")
            if task['children']:
                print_tree(task['children'], indent + 1)

    if not trees:
        click.echo("No tasks found.")
        return

    print_tree(trees)


@cli.command()
@click.argument('task_id', type=int)
@click.argument('linked_task_id', type=int)
@click.option('--type', '-t', default='related', help='Link type')
@click.pass_context
def link(ctx: click.Context, task_id: int, linked_task_id: int, type: str):
    """Link two tasks together."""
    db = ctx.obj['db']
    if db.link_tasks(task_id, linked_task_id, type):
        click.echo(f"Task #{task_id} linked to task #{linked_task_id} ({type}).")
    else:
        click.echo(f"Failed to link tasks. Check that both tasks exist.", err=True)
        raise click.Exit(1)


@cli.command()
@click.argument('task_id', type=int)
@click.argument('linked_task_id', type=int)
@click.pass_context
def unlink(ctx: click.Context, task_id: int, linked_task_id: int):
    """Unlink two tasks."""
    db = ctx.obj['db']
    if db.unlink_tasks(task_id, linked_task_id):
        click.echo(f"Tasks #{task_id} and #{linked_task_id} unlinked.")
    else:
        click.echo(f"No link found between tasks.", err=True)
        raise click.Exit(1)


# Fix ALLOWED_TRANSITIONS access in cancel command
Database.ALLOWED_TRANSITIONS = {
    TaskStatus.PENDING: [TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED, TaskStatus.BLOCKED],
    TaskStatus.IN_PROGRESS: [TaskStatus.COMPLETED, TaskStatus.STOPPED, TaskStatus.PAUSED, TaskStatus.WAITING, TaskStatus.BLOCKED],
    TaskStatus.STOPPED: [TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED],
    TaskStatus.PAUSED: [TaskStatus.IN_PROGRESS],
    TaskStatus.WAITING: [TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED],
    TaskStatus.BLOCKED: [TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED],
    TaskStatus.COMPLETED: [],
    TaskStatus.CANCELLED: [],
}


def main():
    """Entry point for the CLI."""
    cli()
