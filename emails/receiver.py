import imaplib
import email
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailReceiver:
    def __init__(self, config):
        self.config = config
        self.email_settings = config.email_settings

    def check_responses(self):
        """Check for and process email responses"""
        try:
            logger.info(f"Connecting to IMAP server: {self.email_settings['imap_server']}")
            mail = imaplib.IMAP4_SSL(self.email_settings['imap_server'])
            mail.login(self.email_settings['username'], self.email_settings['password'])
            mail.select('inbox')

            # Search for unread responses containing "Weekly Question" instead of exact subject match
            _, messages = mail.search(None, 'UNSEEN SUBJECT "Weekly Question"')
            responses = []
            
            for msg_num in messages[0].split():
                try:
                    _, msg_data = mail.fetch(msg_num, '(RFC822)')
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    # Extract sender information
                    sender_email = email.utils.parseaddr(email_message['from'])[1]
                    
                    # Extract response text
                    response_text = ""
                    for part in email_message.walk():
                        if part.get_content_type() == "text/plain":
                            response_text = part.get_payload(decode=True).decode()
                            break
                    
                    responses.append({
                        "email": sender_email,
                        "response_text": response_text,
                        "timestamp": datetime.utcnow()
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing message {msg_num}: {str(e)}")
                    continue

            mail.close()
            mail.logout()
            return responses
            
        except Exception as e:
            logger.error(f"Error checking email responses: {str(e)}")
            raise
