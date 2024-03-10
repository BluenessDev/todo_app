import click
import uuid

from datetime import datetime

import toudou.models as models
import toudou.services as services
from flask import render_template, Flask, redirect, url_for, request


@click.group()
def cli():
    pass


@cli.command()
def init_db():
    """
    Initialize the database
    :return:
    """
    models.init_db()


@cli.command()
@click.option("-t", "--task", prompt="Your task", help="The task to remember.")
@click.option("-d", "--due", type=click.DateTime(), default=None, help="Due date of the task.")
def create(task: str, due: datetime):
    """
    Create a new todo
    :param task:
    :param due:
    :return:
    """
    models.create_todo(
        task=task,
        due=due
    )


@cli.command()
@click.option("--id", required=True, type=click.UUID, help="Todo's id.")
def get(id: uuid.UUID):
    """
    Get a todo by id
    :param id:
    :return:
    """
    click.echo(models.get_todo(id))


@cli.command()
@click.option("--as-csv", is_flag=True, help="Ouput a CSV string.")
def get_all(as_csv: bool):
    """
    Get all todos
    :param as_csv:
    :return:
    """
    if as_csv:
        click.echo(services.export_to_csv().getvalue())
    else:
        click.echo(models.get_all_todos())


@cli.command()
@click.argument("csv_file", type=click.File("r"))
def import_csv(csv_file):
    """
    Import todos from a CSV file
    :param csv_file:
    :return:
    """
    services.import_from_csv(csv_file)


@cli.command()
@click.option("--id", required=True, type=click.UUID, help="Todo's id.")
@click.option("-c", "--complete", required=True, type=click.BOOL, help="Todo is done or not.")
@click.option("-t", "--task", prompt="Your task", help="The task to remember.")
@click.option("-d", "--due", type=click.DateTime(), default=None, help="Due date of the task.")
def update(id: uuid.UUID, complete: bool, task: str, due: datetime):
    """
    Update a todo
    :param id:
    :param complete:
    :param task:
    :param due:
    :return:
    """
    models.update_todo(id, task, complete, due)


@cli.command()
@click.option("--id", required=True, type=click.UUID, help="Todo's id.")
def delete(id: uuid.UUID):
    """
    Delete a todo
    :param id:
    :return:
    """
    models.delete_todo(id)

# ------------------------------
# GUI web app
# ------------------------------

app = Flask(__name__)

@app.route('/')
def index():
    """
    Index page of the web app
    :return:
    """
    page = request.args.get('page', 1, type=int)
    data = models.get_all_todos_html(page)
    total_tasks = len(models.get_all_todos())
    data['total_tasks'] = total_tasks
    return render_template('index.html', data=data, page=page)

@app.route('/create', methods=['GET', 'POST'])
def create():
    """
    Create a new todo for the web app
    :return:
    """
    if request.method == 'POST':
        task = request.form['task']
        due = request.form['due']
        due = datetime.strptime(due, "%Y-%m-%d") if due else None
        time = request.form['time']
        time = datetime.strptime(time, "%H:%M:%S") if time else None
        due = datetime.combine(due, time.time()) if time else due
        models.create_todo(
            task=task,
            due=due
        )
        return redirect(url_for('index'))


@app.route('/delete/<id>', methods=['GET'])
def delete(id: uuid.UUID):
    """
    Delete a todo by id for the web app
    :param id:
    :return:
    """
    models.delete_todo(id)
    return redirect(url_for('index'))

@app.route('/update/<id>', methods=['GET', 'POST'])
def update(id: uuid.UUID):
    """
    Update a todo by id for the web app
    :param id:
    :return:
    """
    if request.method == 'POST':
        task = request.form['task']
        due = request.form['due']
        due = datetime.strptime(due, "%Y-%m-%d") if due else None
        time = request.form['time']
        time = datetime.strptime(time, "%H:%M:%S") if time else None
        due = datetime.combine(due, time.time()) if time else due
        complete = request.form.get('complete') == 'on'
        models.update_todo(id, task, complete, due)
        return redirect(url_for('index'))
    else:
        data = models.get_all_todos_html(page)
        return render_template('index.html', data=data)

@app.route('/import', methods=['GET', 'POST'])
def import_csv():
    """
    Import todos from a CSV file for the web app
    :return:
    """
    if request.method == 'POST':
        csv_file = request.files['csv_file']
        services.import_from_csv_database(csv_file)
        return redirect(url_for('index'))
    else:
        return render_template('import.html')

@app.route('/export', methods=['POST'])
def export_csv():
    """
    Export todos to a CSV file for the web app
    :return:
    """
    filename = request.form['export']
    filename = f"{filename}.csv" if not filename.endswith('.csv') else filename
    services.export_to_csv_file_db(filename)
    return redirect(url_for('index'))

