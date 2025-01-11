import smtplib
import schedule
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yaml
from email_templates import EmailTemplate
import pandas as pd
from database.response_dao import ResponseDAO
import imaplib
import email
import logging
from utils.health_checker import HealthChecker
import signal
import sys
from utils.rate_limiter import EmailRateLimiter


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FamilyStoriesApp:
    def __init__(self, config_file='config.yml'):
        self.load_config(config_file)
        self.questions = self.load_questions()
        self.response_dao = ResponseDAO()
        self.current_question_index = self.response_dao.get_or_create_question_index()
        self.health_checker = HealthChecker(self)
        self.running = True
        
        # Initialize rate limiter
        rate_limit_config = self.email_settings.get('rate_limit', {})
        self.rate_limiter = EmailRateLimiter(
            max_emails_per_hour=rate_limit_config.get('max_emails_per_hour', 100),
            delay_between_emails=rate_limit_config.get('delay_between_emails', 5)
        )

    def load_config(self, config_file):
        required_settings = {
            'smtp_server': str,
            'smtp_port': int,
            'imap_server': str,
            'username': str,
            'password': str,
            'rate_limit': dict
        }
        
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
            self.email_settings = config.get('email', {})
            
            # Validate types and presence
            for setting, expected_type in required_settings.items():
                if setting not in self.email_settings:
                    raise ValueError(f"Missing required email setting: {setting}")
                if not isinstance(self.email_settings[setting], expected_type):
                    raise TypeError(f"Invalid type for {setting}. Expected {expected_type}")
            
            # Validate rate limit settings
            rate_limit = self.email_settings['rate_limit']
            if not isinstance(rate_limit.get('max_emails_per_hour', 0), int):
                raise TypeError("max_emails_per_hour must be an integer")
            if not isinstance(rate_limit.get('delay_between_emails', 0), (int, float)):
                raise TypeError("delay_between_emails must be a number")
            
        self.family_members = self.load_family_members()
    
    def load_family_members(self, csv_file='emails.csv'):
        try:
            df = pd.read_csv(csv_file)
            return [{'name': name, 'email': email} for name, email in zip(df['name'], df['email'])]
        except Exception as e:
            logger.error(f"Failed to load family members: {str(e)}")
            return []
    
    def load_questions(self, csv_file='questions.csv'):
        try:
            df = pd.read_csv(csv_file)
            return df['question'].tolist()
        except Exception as e:
            print(f"Failed to load questions: {str(e)}")
            return []
    
    def send_email(self, member_email, subject, text_content, html_content):
        msg = MIMEMultipart('alternative')
        msg['From'] = self.email_settings['username']
        msg['To'] = member_email
        msg['Subject'] = subject
        
        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        
        msg.attach(part1)
        msg.attach(part2)
        
        try:
            with smtplib.SMTP(self.email_settings['smtp_server'], 
                             self.email_settings['smtp_port']) as server:
                server.starttls()
                server.login(self.email_settings['username'], 
                           self.email_settings['password'])
                server.send_message(msg)
            logger.info("Email sent successfully to %s", member_email)
        except Exception as e:
            logger.error("Failed to send email: %s", str(e))

    def send_weekly_question(self):
        try:
            current_question = self.questions[self.current_question_index]
            failed_sends = []

            for member in self.family_members:
                retries = 3
                while retries > 0:
                    try:
                        self.rate_limiter.wait_if_needed()
                        text_content, html_content = EmailTemplate.get_email_content(
                            current_question, member['name'])
                        
                        self.send_email(
                            member['email'],
                            "Weekly Family Story Question",
                            text_content,
                            html_content
                        )
                        self.rate_limiter.record_email_sent()
                        break
                    except Exception as e:
                        retries -= 1
                        if retries == 0:
                            failed_sends.append((member['email'], str(e)))
                        time.sleep(1)  # Wait before retry

            if failed_sends:
                logger.error(f"Failed to send to some members: {failed_sends}")
                
            # Update question index only if at least some emails were sent
            if len(failed_sends) < len(self.family_members):
                self.advance_question()
                
            return len(failed_sends) == 0
            
        except Exception as e:
            logger.error(f"Error sending weekly question: {str(e)}")
            return False

    def check_email_responses(self):
        try:
            print(f"Connecting to IMAP server: {self.email_settings['imap_server']}")
            mail = imaplib.IMAP4_SSL(self.email_settings['imap_server'])
            print("Logging in...")
            mail.login(self.email_settings['username'], self.email_settings['password'])
            print("Selecting inbox...")
            mail.select('inbox')

            # Only search for replies (subject starting with "Re:")
            print("Searching for unread response messages...")
            _, messages = mail.search(None, 'UNSEEN SUBJECT "Re: Weekly Family Story Question"')
            
            message_count = len(messages[0].split())
            print(f"Found {message_count} unread responses")

            current_question = self.questions[self.current_question_index]
            
            for msg_num in messages[0].split():
                print(f"Processing message {msg_num}...")
                _, msg_data = mail.fetch(msg_num, '(RFC822)')
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                sender_email = email.utils.parseaddr(email_message['from'])[1]
                
                # Find the family member's name from our list
                sender_name = next(
                    (member['name'] for member in self.family_members 
                     if member['email'] == sender_email),
                    'Unknown'
                )
                print(f"Message from: {sender_name} ({sender_email})")

                response_text = ""
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        response_text = part.get_payload(decode=True).decode()
                        break

                print(f"Storing response from {sender_email}...")
                self.response_dao.store_response(
                    self.current_question_index,
                    sender_email,
                    response_text,
                    sender_name,
                    current_question
                )
                self.send_confirmation_email(sender_email, sender_name, current_question)

            mail.close()
            mail.logout()
            print("Email check completed successfully")

        except Exception as e:
            print(f"Error checking email responses: {str(e)}")
            raise

    def send_confirmation_email(self, member_email, member_name, question):
        msg = MIMEMultipart('alternative')
        msg['From'] = self.email_settings['username']
        msg['To'] = member_email
        msg['Subject'] = "Response Received - Family Story"
        
        # Get confirmation email content from template
        text, html = EmailTemplate.get_confirmation_email_content(member_name, question)
        
        # Attach both plain text and HTML versions
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        
        msg.attach(part1)
        msg.attach(part2)
        
        try:
            with smtplib.SMTP(self.email_settings['smtp_server'], self.email_settings['smtp_port']) as server:
                server.starttls()
                server.login(self.email_settings['username'], self.email_settings['password'])
                server.send_message(msg)
            logger.info(f"Confirmation email sent successfully to {member_email}")
        except Exception as e:
            print(f"Failed to send confirmation email to {member_email}: {str(e)}")

    def health_check(self):
        """
        Run comprehensive health check
        """
        return self.health_checker.check_health()

    def stop(self):
        """Gracefully stop the application"""
        logger.info("Stopping application...")
        self.running = False
        
        # Close database connection
        if hasattr(self, 'response_dao'):
            self.response_dao.db_manager.client.close()
        
        # Cancel any pending scheduled jobs
        schedule.clear()

    def advance_question(self):
        self.current_question_index = (self.current_question_index + 1) % len(self.questions)
        self.response_dao.update_question_index(
            self.current_question_index,
            self.questions[self.current_question_index]
        )

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}")
    if app:
        app.stop()

def main():
    global app  # Make app accessible to signal handler
    app = FamilyStoriesApp()
    
    # Set up signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Schedule weekly question sending (Monday at 9 AM)
        schedule.every().monday.at("09:00").do(app.send_weekly_questions)
        logger.info("Scheduled weekly questions for Monday at 09:00")
        
        # Schedule hourly response checking
        schedule.every().hour.do(app.check_email_responses)
        logger.info("Scheduled hourly response checking")
        
        # Log next run times
        next_question_time = schedule.next_run()
        logger.info(f"Next question will be sent at: {next_question_time}")
        
        logger.info("Application started successfully")
        
        # Main loop
        while app.running:
            schedule.run_pending()
            time.sleep(60)  # Wait one minute between checks
            
    except Exception as e:
        logger.error(f"Fatal error in main loop: {str(e)}")
        app.stop()
        sys.exit(1)
    
    logger.info("Application shutdown complete")
    sys.exit(0)

if __name__ == "__main__":
    main()
