import os
import pickle
import uuid

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import sqlite3
import math

from sqlalchemy import Table, MetaData, create_engine, Column, Uuid, String, Boolean, DateTime

TODO_FOLDER = "db"

engine = create_engine("sqlite:///todos.db", echo=True)
metadata = MetaData()

todos_table = Table(
    "todos",
    metadata,
    Column("id", Uuid, primary_key=True, default=uuid.uuid4),
    Column("task", String, nullable=False),
    Column("complete", Boolean, nullable=False),
    Column("due", DateTime, nullable=True)
)


@dataclass
class Todo:
    id: uuid.UUID
    task: str
    complete: bool
    due: Optional[datetime]


def init_db() -> None:
    """
    Initialize the database
    :return:
    """
    conn = sqlite3.connect("todos.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS todos (
            id TEXT PRIMARY KEY,
            task TEXT NOT NULL,
            complete BOOLEAN NOT NULL,
            due TIMESTAMP
        )
        """
    )


def read_from_file(filename: str) -> Todo:
    """
    Read a todo from a file (pickle)
    :param filename:
    :return:
    """
    with open(os.path.join(TODO_FOLDER, filename), "rb") as f:
        return pickle.load(f)


def read_from_db() -> list[Todo]:
    """
    Read all todos from the database
    :return:
    """
    stmt = todos_table.select()

    with engine.begin() as conn:
        result = conn.execute(stmt)
        return result.fetchall()


def write_to_file(todo: Todo, filename: str) -> None:
    """
    Write a todo to a file (pickle)
    :param todo:
    :param filename:
    :return:
    """
    with open(os.path.join(TODO_FOLDER, filename), "wb") as f:
        pickle.dump(todo, f)


def write_to_db(todo: Todo) -> None:
    """
    Write a todo to the database
    :param todo:
    :return:
    """
    stmt = todos_table.insert().values(
        id=todo.id,
        task=todo.task,
        complete=todo.complete,
        due=todo.due
    )

    with engine.begin() as conn:
        result = conn.execute(stmt)


def create_todo(
        task: str,
        complete: bool = False,
        due: Optional[datetime] = None
) -> None:
    """
    Create a new todo and write it to the database
    :param task:
    :param complete:
    :param due:
    :return:
    """
    stmt = todos_table.insert().values(
        task=task,
        complete=complete,
        due=due
    )

    with engine.begin() as conn:
        result = conn.execute(stmt)


def get_todo(id: uuid.UUID) -> Todo:
    """
    Get a todo by id from the database
    :param id:
    :return:
    """
    stmt = todos_table.select().where(todos_table.c.id == id)

    with engine.begin() as conn:
        result = conn.execute(stmt)
        return result.fetchone()


def get_all_todos() -> list[Todo]:
    """
    Get all todos from the database
    :return:
    """
    stmt = todos_table.select()

    with engine.begin() as conn:
        result = conn.execute(stmt)
        return result.fetchall()


def get_all_todos_export() -> list[Todo]:
    """
    Get all todos from the database for export
    :return:
    """
    stmt = todos_table.select()

    with engine.begin() as conn:
        result = conn.execute(stmt)
        rows = result.fetchall()

    return [Todo(
        id=row.id,
        task=row.task,
        complete=row.complete,
        due=row.due
    ) for row in rows]


def get_all_todos_html(page: int = 1, per_page: int = 6) -> dict:
    """
    Get all todos from the database for the web app with pagination
    :param page:
    :param per_page:
    :return:
    """
    stmt = todos_table.select()

    with engine.begin() as conn:
        result = conn.execute(stmt)
        all_todos = result.fetchall()

    start = (page - 1) * per_page
    end = start + per_page
    todos = all_todos[start:end]

    total_pages = math.ceil(len(all_todos) / per_page)

    return {
        'todos': todos,
        'has_prev': start > 0,
        'has_next': end < len(all_todos),
        'prev_num': page - 1 if start > 0 else None,
        'next_num': page + 1 if end < len(all_todos) else None,
        'total_pages': total_pages,
    }


def update_todo(
        id: str,
        task: str,
        complete: bool,
        due: Optional[datetime]
) -> None:
    """
    Update a todo in the database by id with new values
    :param id:
    :param task:
    :param complete:
    :param due:
    :return:
    """
    if not isinstance(id, uuid.UUID):
        id = uuid.UUID(id)
    stmt = todos_table.update().where(todos_table.c.id == id).values(
        task=task,
        complete=complete,
        due=due
    )

    with engine.begin() as conn:
        result = conn.execute(stmt)


def delete_todo(id: str) -> None:
    """
    Delete a todo from the database by id
    :param id:
    :return:
    """
    if not isinstance(id, uuid.UUID):
        id = uuid.UUID(id)
    stmt = todos_table.delete().where(todos_table.c.id == id)

    with engine.begin() as conn:
        result = conn.execute(stmt)


def clear_database() -> None:
    """
    Clear all todos from the database
    :return:
    """
    stmt = todos_table.delete()

    with engine.begin() as conn:
        result = conn.execute(stmt)