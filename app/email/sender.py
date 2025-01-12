from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import logging
from app.email.templates import EmailTemplate

logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self, config):
        self.config = config
        self.email_settings = config.email_settings
        
    def send_email(self, to_email, subject, text_content, html_content):
        msg = MIMEMultipart('alternative')
        msg['From'] = self.email_settings['username']
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        try:
            with smtplib.SMTP(self.email_settings['smtp_server'], 
                             self.email_settings['smtp_port']) as server:
                server.starttls()
                server.login(self.email_settings['username'], 
                           self.email_settings['password'])
                server.send_message(msg)
            logger.info(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    def send_weekly_question(self, question, quote, family_members):
        failed_sends = []
        
        for member in family_members:
            text_content, html_content = EmailTemplate.get_email_content(
                question['question'],
                member['name'],
                question['questioner'],
                quote['quote'],
                quote['author']
            )
            
            success = self.send_email(
                member['email'],
                "Weekly Family Story Question",
                text_content,
                html_content
            )
            
            if not success:
                failed_sends.append(member['email'])
        
        if failed_sends:
            logger.error(f"Failed to send to: {failed_sends}")
        
        return len(failed_sends) == 0

    def send_confirmation_email(self, email, name, question):
        text_content, html_content = EmailTemplate.get_confirmation_email_content(
            name,
            question
        )
        
        return self.send_email(
            email,
            "Response Received - Family Story",
            text_content,
            html_content
        )
