from app.email.sender import EmailSender
from app.email.receiver import EmailReceiver
from app.database.dao import ResponseDAO
from app.utils.health_checker import HealthChecker
from app.utils.rate_limiter import EmailRateLimiter
from app.core.config import Config
import logging
import schedule

logger = logging.getLogger(__name__)

class FamilyStoriesApp:
    VERSION = "1.0.0"
    
    def __init__(self, config_file='config.yml'):
        self.version = self.VERSION
        self.config = Config(config_file)
        self.email_sender = EmailSender(self.config)
        self.email_receiver = EmailReceiver(self.config)
        self.response_dao = ResponseDAO(self.config)
        self.health_checker = HealthChecker(self)
        self.running = True
        
        self.questions = self.config.load_questions()
        self.quotes = self.config.load_quotes()
        self.family_members = self.config.load_family_members()
        self.current_question_index = self.response_dao.get_or_create_question_index()

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
            responses = self.email_receiver.check_responses()
            for response in responses:
                self.response_dao.store_response(**response)
                self.email_sender.send_confirmation_email(
                    response['email'],
                    response['sender_name'],
                    response['question']
                )
        except Exception as e:
            logger.error(f"Error checking responses: {str(e)}")
            raise

    def health_check(self):
        return self.health_checker.check_health()

    def stop(self):
        logger.info("Stopping application...")
        self.running = False
        self.response_dao.close()
        schedule.clear()

    def advance_question(self):
        if not self.questions:
            logger.error("Cannot advance question: No questions loaded")
            return False
        
        self.current_question_index = (self.current_question_index + 1) % len(self.questions)
        self.response_dao.update_question_index(
            self.current_question_index,
            self.questions[self.current_question_index]
        )
        return True
