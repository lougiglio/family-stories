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
            logger.debug(f"Attempting to connect to SMTP server {self.smtp_server}:{self.smtp_port}")
            
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
            
            # Send email with detailed logging
            try:
                logger.debug("Creating SMTP connection...")
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                
                logger.debug("Starting TLS...")
                server.starttls()
                
                logger.debug(f"Attempting login for user {self.username}")
                server.login(self.username, self.password)
                
                logger.debug("Sending message...")
                server.send_message(msg)
                
                logger.debug("Closing connection...")
                server.quit()
                
                logger.info(f"Successfully sent weekly question to {recipient_email}")
                
            except smtplib.SMTPAuthenticationError as auth_error:
                logger.error(f"SMTP Authentication failed: {str(auth_error)}")
                raise
            except smtplib.SMTPException as smtp_error:
                logger.error(f"SMTP error occurred: {str(smtp_error)}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error during SMTP operation: {str(e)}")
                raise
            
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

    def forward_response(self, sender_email, sender_name, response_text, question, recipients):
        """Forward a family member's response to a list of recipients"""
        try:
            logger.info(f"Forwarding response from {sender_email} to {len(recipients)} recipients")
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Family Story Response: {sender_name}"
            msg['From'] = self.username
            
            # Preprocess the response text to replace newlines with <br> tags
            formatted_response = response_text.replace('\n', '<br>')
            
            # Create HTML content
            html_head = """
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { color: #2c3e50; margin-bottom: 20px; }
                    .question { font-style: italic; color: #7f8c8d; margin-bottom: 15px; }
                    .response { background-color: #f9f9f9; padding: 15px; border-left: 4px solid #3498db; margin-bottom: 20px; }
                    .footer { font-size: 0.9em; color: #7f8c8d; margin-top: 30px; border-top: 1px solid #eee; padding-top: 10px; }
                </style>
            </head>
            """
            
            # Now use f-strings for the dynamic content
            html_body = f"""
            <body>
                <div class="container">
                    <h2 class="header">Family Story Response</h2>
                    <p>{sender_name} has shared a response to our family story question:</p>
                    
                    <div class="question">
                        <strong>Question:</strong> {question}
                    </div>
                    
                    <div class="response">
                        <strong>{sender_name}'s Response:</strong><br><br>
                        {formatted_response}
                    </div>
                    
                    <div class="footer">
                        <p>This is an automated message from the Family Stories app.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Combine the HTML parts
            html_content = html_head + html_body
            
            # Attach HTML version
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send to each recipient
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                
                for recipient in recipients:
                    try:
                        # Set recipient for this specific email
                        msg['To'] = recipient['email']
                        server.send_message(msg)
                        logger.info(f"Successfully forwarded response to {recipient['email']}")
                        
                        # Clear the 'To' field for the next recipient
                        del msg['To']
                        
                    except Exception as e:
                        logger.error(f"Failed to forward response to {recipient['email']}: {str(e)}")
                        # Continue with other recipients even if one fails
                        continue
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to forward response: {str(e)}")
            return False
