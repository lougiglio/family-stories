from datetime import datetime
import logging
import time
from database import DatabaseManager

logger = logging.getLogger(__name__)

class ResponseDAO:
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds

    def __init__(self, config=None):
        self.db_manager = DatabaseManager(config)
        self.db = self.db_manager.db

    def _execute_with_retry(self, operation):
        """Execute database operation with retry logic"""
        for attempt in range(self.MAX_RETRIES):
            try:
                return operation()
            except Exception as e:
                if attempt == self.MAX_RETRIES - 1:
                    logger.error(f"Database operation failed after {self.MAX_RETRIES} attempts: {str(e)}")
                    raise
                logger.warning(f"Database operation failed, attempt {attempt + 1}: {str(e)}")
                time.sleep(self.RETRY_DELAY)

    def store_response(self, question_index, email, response_text, sender_name, question):
        """Store response with retry logic"""
        def operation():
            return self.db.responses.insert_one({
                "question_index": question_index,
                "family_member_email": email,
                "response_text": response_text,
                "sender_name": sender_name,
                "question": question,
                "timestamp": datetime.utcnow()
            })
        return self._execute_with_retry(operation)

    def get_or_create_question_index(self):
        """Get current question index or create if not exists"""
        def operation():
            result = self.db.app_state.find_one({"_id": "question_index"})
            if not result:
                self.db.app_state.insert_one({
                    "_id": "question_index",
                    "current_index": 0
                })
                return 0
            return result["current_index"]
        return self._execute_with_retry(operation)

    def update_question_index(self, new_index, question):
        """Update the current question index"""
        def operation():
            return self.db.app_state.update_one(
                {"_id": "question_index"},
                {
                    "$set": {
                        "current_index": new_index,
                        "last_updated": datetime.utcnow(),
                        "current_question": question
                    }
                }
            )
        return self._execute_with_retry(operation)

    def close(self):
        """Close database connection"""
        if hasattr(self, 'db_manager'):
            self.db_manager.client.close()
