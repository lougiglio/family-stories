import pytest
from unittest.mock import Mock, patch
from app.database.dao import ResponseDAO
from datetime import datetime

@pytest.fixture
def dao():
    with patch('app.database.db_config.DatabaseManager') as MockDB:
        mock_instance = MockDB.return_value
        mock_instance.db_settings = {
            'mongodb_uri': 'mongodb://test:test@localhost:27017',
            'database_name': 'test_db'
        }
        mock_instance.db = Mock()
        mock_instance.connect = Mock()
        mock_instance.client = Mock()
        
        dao = ResponseDAO()
        dao.db_manager = mock_instance
        dao.db = mock_instance.db
        return dao

def test_store_response(dao):
    response_data = {
        'question_index': 0,
        'email': 'test@example.com',
        'response_text': 'Test response',
        'sender_name': 'Test User',
        'question': 'Test question?'
    }
    
    dao.store_response(**response_data)
    dao.db.responses.insert_one.assert_called_once()

def test_get_question_index(dao):
    dao.db.app_state.find_one.return_value = {'current_index': 5}
    index = dao.get_or_create_question_index()
    assert index == 5

def test_update_question_index(dao):
    dao.update_question_index(1, 'New question?')
    dao.db.app_state.update_one.assert_called_once() 