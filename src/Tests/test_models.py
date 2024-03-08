import unittest
from datetime import datetime
from unittest.mock import patch
import uuid
import src.toudou.models as models


class TestToudouModels(unittest.TestCase):

    @patch('src.toudou.models.todos_table')
    @patch('src.toudou.models.engine')
    def test_get_todo_retrieves_correct_data(self, mock_engine, mock_table):
        mock_conn = mock_engine.begin.return_value.__enter__.return_value
        todo_id = uuid.uuid4()

        models.get_todo(todo_id)

        mock_table.select.assert_called_once()
        mock_conn.execute.assert_called_once_with(mock_table.select.return_value.where.return_value)

    @patch('src.toudou.models.todos_table')
    @patch('src.toudou.models.engine')
    def test_update_todo_updates_correct_data(self, mock_engine, mock_table):
        mock_conn = mock_engine.begin.return_value.__enter__.return_value
        todo_id = uuid.uuid4()
        task = "Updated task"
        complete = True
        due = datetime.now()

        models.update_todo(todo_id, task, complete, due)

        mock_table.update.assert_called_once()
        mock_conn.execute.assert_called_once_with(mock_table.update.return_value.where.return_value.values.return_value)

    @patch('src.toudou.models.todos_table')
    @patch('src.toudou.models.engine')
    def test_delete_todo_deletes_correct_data(self, mock_engine, mock_table):
        mock_conn = mock_engine.begin.return_value.__enter__.return_value
        todo_id = uuid.uuid4()

        models.delete_todo(todo_id)

        mock_table.delete.assert_called_once()
        mock_conn.execute.assert_called_once_with(mock_table.delete.return_value.where.return_value)


if __name__ == '__main__':
    unittest.main()