import pytest
from unittest.mock import Mock, patch
from app.email.sender import EmailSender
from app.email.receiver import EmailReceiver

@pytest.fixture
def email_config():
    return {
        'smtp_server': 'smtp.test.com',
        'smtp_port': 587,
        'imap_server': 'imap.test.com',
        'username': 'test@example.com',
        'password': 'test_password',
        'rate_limit': {
            'max_emails_per_hour': 100,
            'delay_between_emails': 1
        }
    }

@pytest.fixture
def sender(email_config):
    config = Mock()
    config.email_settings = email_config
    return EmailSender(config)

@pytest.fixture
def receiver(email_config):
    config = Mock()
    config.email_settings = email_config
    return EmailReceiver(config)

def test_send_email(sender):
    with patch('smtplib.SMTP') as mock_smtp:
        mock_smtp.return_value.__enter__.return_value = mock_smtp.return_value
        result = sender.send_email(
            'test@example.com',
            'Test Subject',
            'Test content',
            '<p>Test content</p>'
        )
        assert result == True
        mock_smtp.return_value.send_message.assert_called_once()

def test_check_responses(receiver):
    with patch('imaplib.IMAP4_SSL') as mock_imap:
        mock_imap.return_value.search.return_value = (None, [b'1'])
        mock_imap.return_value.fetch.return_value = (None, [(b'', b'')])
        responses = receiver.check_responses()
        assert isinstance(responses, list) 