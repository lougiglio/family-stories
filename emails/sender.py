from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import logging
from .templates import WeeklyQuestionEmail, ConfirmationEmail

logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self, smtp_server, smtp_port, username, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def send_weekly_question(self, recipient_email, recipient_name, questioner_name, question, quote, quote_author, question_number=None):
        """Send weekly question email to a family member"""
        try:
            logger.info(f"Sending weekly question to {recipient_email}")
            
            # Get email content
            html_content = WeeklyQuestionEmail.get_content(
                question=question,
                recipient_name=recipient_name,
                questioner_name=questioner_name,
                quote=quote,
                quote_author=quote_author,
                question_number=question_number
            )
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Family Stories - Weekly Question #{question_number:02d}"
            msg['From'] = self.username
            msg['To'] = recipient_email
            
            # Attach HTML version
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
                
            logger.info(f"Successfully sent weekly question to {recipient_email}")
            
        except Exception as e:
            logger.error(f"Failed to send weekly question to {recipient_email}: {str(e)}")
            raise

    def send_confirmation(self, recipient_email, recipient_name, question):
        """Send confirmation email after receiving a response"""
        try:
            logger.info(f"Sending confirmation to {recipient_email}")
            
            # Get email content
            html_content = ConfirmationEmail.get_content(
                recipient_name=recipient_name,
                question=question
            )
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "Thank You for Sharing Your Story"
            msg['From'] = self.username
            msg['To'] = recipient_email
            
            # Attach HTML version
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
                
            logger.info(f"Successfully sent confirmation to {recipient_email}")
            
        except Exception as e:
            logger.error(f"Failed to send confirmation to {recipient_email}: {str(e)}")
            raise
