from emails.sender import EmailSender
from emails.receiver import EmailReceiver
from database import DatabaseManager
from build.config import Config
import logging
import schedule
import signal
import sys
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class FamilyStoriesApp:
    VERSION = "1.0.0"
    
    def __init__(self, config_file='build/config.yml'):
        self.version = self.VERSION
        self.config = Config(config_file)
        self.email_sender = EmailSender(
            smtp_server=self.config.email_settings['smtp_server'],
            smtp_port=self.config.email_settings['smtp_port'],
            username=self.config.email_settings['username'],
            password=self.config.email_settings['password']
        )
        self.email_receiver = EmailReceiver(self.config)
        self.database = DatabaseManager(self.config)
        self.running = True
        
        self.questions = self.config.load_questions()
        self.quotes = self.config.load_quotes()
        self.family_members = self.config.load_family_members()
        self.current_question_index = self.database.get_or_create_question_index()
        
        # Set up signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}")
        self.stop()

    def send_weekly_question(self):
        try:
            current_question = self.questions[self.current_question_index]
            current_quote = self.quotes[self.current_question_index % len(self.quotes)]
            
            success = self.email_sender.send_weekly_question(
                current_question,
                current_quote,
                self.family_members
            )
            
            if success:
                self.advance_question()
            return success
            
        except Exception as e:
            logger.error(f"Error sending weekly question: {str(e)}")
            return False

    def check_email_responses(self):
        try:
            logger.info("Checking for email responses...")
            responses = self.email_receiver.check_responses()
            logger.info(f"Found {len(responses)} new responses")
            
            current_question = self.questions[self.current_question_index]
            
            for response in responses:
                logger.info(f"Processing response from {response['email']}")
                # Add current question to the response storage
                self.database.store_response(
                    email=response['email'],
                    response_text=response['response_text'],
                    timestamp=response['timestamp'],
                    question=current_question
                )
                logger.info(f"Successfully stored response from {response['email']} in database")
                
                try:
                    self.email_sender.send_confirmation_email(
                        response['email'],
                        response.get('sender_name', 'Family Member'),
                        current_question['question']  # Use actual question text
                    )
                    logger.info(f"Sent confirmation email to {response['email']}")
                except Exception as e:
                    logger.error(f"Failed to send confirmation email: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error checking responses: {str(e)}")
            raise

    def stop(self):
        logger.info("Stopping application...")
        self.running = False
        self.database.close()
        schedule.clear()

    def advance_question(self):
        if not self.questions:
            logger.error("Cannot advance question: No questions loaded")
            return False
        
        self.current_question_index = (self.current_question_index + 1) % len(self.questions)
        self.database.update_question_index(
            self.current_question_index,
            self.questions[self.current_question_index]
        )
        return True

    def run(self):
        """Main entry point to run the application"""
        try:
            # Schedule weekly question sending (Sunday at 6 AM)
            schedule.every().sunday.at("06:00").do(self.send_weekly_question)
            logger.info("Scheduled weekly questions for Sunday at 06:00")
            
            # Schedule response checking every 15 minutes, but only between 6 AM and 10 PM
            for hour in range(6, 22):  # 6 AM to 10 PM
                for minute in [0, 15, 30, 45]:
                    schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(self.check_email_responses)
            logger.info("Scheduled response checking every 15 minutes between 6 AM and 10 PM")
            
            logger.info("Application started successfully")
            
            # Run email check immediately on startup if within active hours
            current_hour = datetime.now().hour
            if 6 <= current_hour < 22:
                self.check_email_responses()
            
            # Main loop
            while self.running:
                schedule.run_pending()
                time.sleep(60)
                
        except Exception as e:
            logger.error(f"Fatal error in main loop: {str(e)}")
            self.stop()
            sys.exit(1)
        
        logger.info("Application shutdown complete")
        sys.exit(0)

def main():
    app = FamilyStoriesApp()
    
    # Send a test email immediately
    logger.info("Sending test email...")
    success = app.send_weekly_question()
    if success:
        logger.info("Test email sent successfully!")
    else:
        logger.error("Failed to send test email")
    
    app.run()

if __name__ == "__main__":
    main()
