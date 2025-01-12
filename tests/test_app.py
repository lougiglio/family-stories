import pytest
from unittest.mock import Mock, patch
from app.core.app import FamilyStoriesApp
from datetime import datetime

@pytest.fixture
def mock_config():
    return {
        'email': {
            'smtp_server': 'smtp.test.com',
            'smtp_port': 587,
            'imap_server': 'imap.test.com',
            'username': 'test@example.com',
            'password': 'test_password',
            'rate_limit': {
                'max_emails_per_hour': 100,
                'delay_between_emails': 1
            }
        },
        'database': {
            'mongodb_uri': 'mongodb://test:test@localhost:27017',
            'database_name': 'app_test'
        }
    }

@pytest.fixture
def app(mock_config):
    with patch('app.core.config.Config') as MockConfig:
        mock_instance = Mock()
        mock_instance.config = mock_config
        mock_instance.db_settings = mock_config['database']
        mock_instance.email_settings = mock_config['email']
        
        MockConfig.return_value = mock_instance
        
        app = FamilyStoriesApp()
        app.questions = ['Test Question?']
        app.quotes = ['Test Quote']
        app.family_members = [{'name': 'Test User', 'email': 'test@example.com'}]
        return app

def test_app_initialization(app):
    assert app.version == FamilyStoriesApp.VERSION
    assert app.running == True
    assert len(app.questions) > 0
    assert len(app.quotes) > 0
    assert len(app.family_members) > 0

def test_send_weekly_question(app):
    with patch('app.email.sender.EmailSender.send_email') as mock_send:
        mock_send.return_value = True
        result = app.send_weekly_question()
        assert result == True
        mock_send.assert_called()

def test_check_email_responses(app):
    with patch('app.email.receiver.EmailReceiver.check_responses') as mock_check:
        mock_check.return_value = [{
            'email': 'test@example.com',
            'response_text': 'Test response',
            'timestamp': datetime.now()
        }]
        app.check_email_responses()
        mock_check.assert_called_once()

def test_health_check(app):
    result = app.health_check()
    assert isinstance(result, dict)
    assert 'healthy' in result
    assert 'checks' in result
    assert 'timestamp' in result

def test_stop(app):
    app.stop()
    assert app.running == False 