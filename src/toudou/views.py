import click
import uuid

from datetime import datetime
from io import TextIOWrapper

from io import BytesIO
import flask
import toudou.models as models
import secrets
import toudou.services as services
from flask import render_template, Flask, redirect, url_for, request, Blueprint, abort, flash, send_file, make_response, Response

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


@cli.command()
def clear():
    """
    Clear the database
    :return:
    """
    models.clear_database()


# ------------------------------
# GUI web app
# ------------------------------

web_ui = Blueprint('web_ui', __name__, url_prefix='/')


def generate_secret_key():
    return secrets.token_hex(32)


def create_app():
    app = Flask(__name__)
    app.secret_key = generate_secret_key()
    app.register_blueprint(web_ui)
    return app


@web_ui.errorhandler(500)
def handle_internal_error(error):
    flash("Page < 1 : Abandon du chargement d'index", "error")
    return redirect(url_for("web_ui.index", page=request.args.get('page', 1)))


@web_ui.errorhandler(501)
def handle_internal_error(error):
    flash("Correspondance incorrecte entre les deux tickets", "error")
    return redirect(url_for("web_ui.index", page=request.args.get('page', 1)))


@web_ui.errorhandler(502)
def handle_internal_error(error):
    flash("Méthode HTTP non autorisée", "error")
    return redirect(url_for("web_ui.index", page=request.args.get('page', 1)))


@web_ui.route('/', methods=['GET'])
def index():
    """
    Index page of the web app
    :return:
    """
    page = request.args.get('page', 1, type=int)
    abort(500) if page < 1 else None
    data = models.get_paginated_todos_for_web(page)
    total_tasks = len(models.get_all_todos())
    data['total_tasks'] = total_tasks
    return render_template('index.html', data=data, page=page)


@web_ui.route('/create', methods=['GET', 'POST'])
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
        return redirect(url_for('web_ui.index', page=request.args.get('page', 1)))


@web_ui.route('/delete/<uuid:id>', methods=['POST'])
def delete(id: uuid.UUID):
    """
    Delete a todo by id for the web app
    :param id:
    :return:
    """
    identifiant = request.form['identifiant']
    if not identifiant or identifiant != str(id):
        abort(501)
    identifiant = uuid.UUID(identifiant)
    todo = models.get_todo(identifiant)
    if not todo:
        abort(501)
    models.delete_todo(identifiant)
    return redirect(url_for('web_ui.index', page=request.args.get('page', 1)))


@web_ui.route('/update/<uuid:id>', methods=['GET', 'POST'])
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
        return redirect(url_for('web_ui.index', page=request.args.get('page', 1)))
    else:
        abort(502)


@web_ui.route('/import', methods=['POST'])
def import_csv():
    """
    Import todos from a CSV file for the web app
    :return:
    """
    csv_file = request.files['file']
    csv_file = TextIOWrapper(csv_file, encoding='utf-8')
    models.clear_database()
    services.import_from_csv_database(csv_file)
    return redirect(url_for('web_ui.index', page=request.args.get('page', 1)))


@web_ui.route('/export', methods=['POST'])
def export_csv():
    """
    Export todos to a CSV file for the web app
    :return:
    """
    filename = request.form['export']
    filename = f"{filename}.csv" if not filename.endswith('.csv') else filename
    csv_file = services.export_to_csv_file_db()
    csv_content = csv_file.getvalue().encode()  # Convert string to bytes
    csv_bytes_io = BytesIO(csv_content)
    response = make_response(send_file(csv_bytes_io, mimetype='text/csv', as_attachment=True, download_name=filename))
    response.headers.set('Content-Disposition', 'attachment', filename=filename)
    return response