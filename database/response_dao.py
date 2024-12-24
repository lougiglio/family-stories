from datetime import datetime
from bson.objectid import ObjectId
from .db_config import DatabaseManager

class ResponseDAO:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.db = self.db_manager.db

    def store_response(self, question_id, sender_email, response_text, sender_name, question_text):
        """Store response in MongoDB"""
        try:
            response_doc = {
                "question_id": question_id,
                "question_text": question_text,
                "family_member_email": sender_email,
                "family_member_name": sender_name,
                "response_text": response_text,
                "response_date": datetime.now()
            }

            result = self.db.responses.insert_one(response_doc)
            return result.inserted_id

        except Exception as e:
            print(f"Error storing response: {str(e)}")
            raise

    def get_response(self, response_id):
        """Retrieve a response"""
        try:
            response = self.db.responses.find_one({"_id": ObjectId(response_id)})
            return response

        except Exception as e:
            print(f"Error retrieving response: {str(e)}")
            raise

    def get_responses_by_question(self, question_id):
        """Get all responses for a specific question"""
        return list(self.db.responses.find({"question_id": question_id}))

    def get_responses_by_email(self, email):
        """Get all responses from a specific family member"""
        return list(self.db.responses.find({"family_member_email": email})) 