import csv
import dataclasses
import io

from datetime import datetime

from toudou.models import create_todo, get_all_todos_export, Todo


def export_to_csv() -> io.StringIO:
    output = io.StringIO()
    csv_writer = csv.DictWriter(
        output,
        fieldnames=[f.name for f in dataclasses.fields(Todo)]
    )
    for todo in get_all_todos():
        csv_writer.writerow(dataclasses.asdict(todo))
    return output


# import le csv dans la base de données
def import_from_csv_database(csv_file: io.StringIO) -> None:
    csv_reader = csv.DictReader(
        csv_file,
        fieldnames=[f.name for f in dataclasses.fields(Todo)]
    )
    for row in csv_reader:
        create_todo(
            task=row["task"],
            due=datetime.fromisoformat(row["due"]) if row["due"] else None,
            complete=row["complete"] == "True"
        )


# exporte la base de données dans un fichier csv avec un nom donné
def export_to_csv_file_db(filename: str) -> None:
    todos = get_all_todos_export()
    print(todos)  # Temporary print statement to debug the content of todos
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = [f.name for f in dataclasses.fields(Todo)]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for todo in todos:
            writer.writerow(dataclasses.asdict(todo))  # Convert todo object to dictionary

def import_from_csv(csv_file: io.StringIO) -> None:
    csv_reader = csv.DictReader(
        csv_file,
        fieldnames=[f.name for f in dataclasses.fields(Todo)]
    )
    for row in csv_reader:
        create_todo(
            task=row["task"],
            due=datetime.fromisoformat(row["due"]) if row["due"] else None,
            complete=row["complete"] == "True"
        )
