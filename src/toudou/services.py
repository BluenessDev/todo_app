import csv
import dataclasses
import io
import uuid

from datetime import datetime

from toudou.models import create_todo, get_all_todos_export, Todo, write_to_db


def import_from_csv_database(csv_file: io.StringIO) -> None:
    csv_reader = csv.DictReader(
        csv_file,
        fieldnames=[f.name for f in dataclasses.fields(Todo)]
    )
    next(csv_reader)  # Skip the header row
    for row in csv_reader:
        try:
            # Verify the format of the data
            id = uuid.UUID(row["id"])
            task = row["task"]
            due = datetime.fromisoformat(row["due"]) if row["due"] else None
            complete = row["complete"] == "True"
        except ValueError:
            print(f"Skipping row due to incorrect format: {row}")
            continue

        todo = Todo(
            id=id,
            task=task,
            due=due,
            complete=complete
        )
        write_to_db(todo)


def export_to_csv_file_db(filename: str) -> None:
    todos = get_all_todos_export()
    print(todos)  # Temporary print statement to debug the content of todos
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = [f.name for f in dataclasses.fields(Todo)]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for todo in todos:
            writer.writerow(dataclasses.asdict(todo))  # Convert todo object to dictionary
