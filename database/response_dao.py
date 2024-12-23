from datetime import datetime
from bson.objectid import ObjectId
from .db_config import DatabaseManager

class ResponseDAO:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.db = self.db_manager.db
        self.fs = self.db_manager.fs

    def store_response(self, question_id, sender_email, response_text, media_files=None):
        """Store response and media files in MongoDB"""
        try:
            response_doc = {
                "question_id": question_id,
                "family_member_email": sender_email,
                "response_text": response_text,
                "response_date": datetime.now(),
                "media_files": []
            }

            if media_files:
                for media_file in media_files:
                    file_id = self.fs.put(
                        media_file['content'],
                        filename=media_file['filename'],
                        content_type=media_file['content_type'],
                        metadata={
                            "original_filename": media_file['filename'],
                            "content_type": media_file['content_type'],
                            "upload_date": datetime.now()
                        }
                    )

                    response_doc["media_files"].append({
                        "file_id": file_id,
                        "filename": media_file['filename'],
                        "content_type": media_file['content_type']
                    })

            result = self.db.responses.insert_one(response_doc)
            return result.inserted_id

        except Exception as e:
            print(f"Error storing response: {str(e)}")
            raise

    def get_response(self, response_id, include_media=False):
        """Retrieve a response and optionally its media files"""
        try:
            response = self.db.responses.find_one({"_id": ObjectId(response_id)})
            if not response:
                return None

            if include_media:
                for media_file in response.get("media_files", []):
                    grid_out = self.fs.get(media_file["file_id"])
                    media_file["data"] = grid_out.read()

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