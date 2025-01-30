import re
import logging
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

logger = logging.getLogger(__name__)

class DatabaseManager:
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds

    def __init__(self, config=None):
        if not config or not config.db_settings:
            raise ValueError("Database configuration is required")
        self.db_settings = config.db_settings
        self.connect()

    def connect(self):
        """Establish database connection with connection pooling"""
        try:
            if not self.db_settings.get('mongodb_uri'):
                raise ValueError("MongoDB URI is missing")
            
            logger.info(f"Connecting to database: {self.db_settings['database_name']}")
            
            # Only try to mask password if URI contains authentication info
            safe_uri = self.db_settings['mongodb_uri']
            if '@' in safe_uri:
                safe_uri = safe_uri.replace(
                    re.search(r':(.+?)@', self.db_settings['mongodb_uri']).group(1),
                    '****'
                )
            logger.debug(f"Using connection string: {safe_uri}")
            
            self.client = MongoClient(
                self.db_settings['mongodb_uri'],
                maxPoolSize=50,
                waitQueueTimeoutMS=2500,
                connectTimeoutMS=2000,
                serverSelectionTimeoutMS=3000,
                retryWrites=True
            )
            
            # Test connection before proceeding
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB server")
            
            self.db = self.client[self.db_settings['database_name']]
            self.setup_collections()
            
            logger.info(f"Successfully initialized database: {self.db_settings['database_name']}")
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
        except OperationFailure as e:
            if "Authentication failed" in str(e):
                logger.error("MongoDB authentication failed. Please check your username and password.")
            else:
                logger.error(f"MongoDB operation failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to database: {str(e)}")
            raise

    def setup_collections(self):
        """Set up collections and their indexes"""
        # Compound index for common query patterns
        self.db.responses.create_index([
            ("question_id", 1),
            ("family_member_email", 1),
            ("response_date", -1)
        ])
        
        # Additional single-field indexes for other query patterns
        self.db.responses.create_index([("question_text", 1)])  # Search by question text
        self.db.responses.create_index([("family_member_name", 1)])  # Search by family member name
        self.db.responses.create_index([("response_date", -1)])  # Pure date-based queries
        
        # Text index for potential full-text search of responses
        self.db.responses.create_index([("response_text", "text")])  # Enable text search in responses
        
        # Family members collection
        self.db.family_members.create_index([
            ("email", 1)
        ], unique=True)
        self.db.family_members.create_index([("name", 1)])  # Search by name
        
        # Set up app_state collection
        self.db.app_state.update_one(
            {"_id": "question_index"},
            {"$setOnInsert": {
                "current_index": 0
            }},
            upsert=True
        )

    def close(self):
        """Close database connection"""
        if hasattr(self, 'client'):
            self.client.close()

    def get_or_create_question_index(self):
        """Get the current question index or create it if it doesn't exist"""
        result = self.db.app_state.find_one({"_id": "question_index"})
        if result is None:
            self.db.app_state.insert_one({
                "_id": "question_index",
                "current_index": 0
            })
            return 0
        return result.get("current_index", 0)

    def update_question_index(self, index, question):
        """Update the current question index"""
        self.db.app_state.update_one(
            {"_id": "question_index"},
            {"$set": {
                "current_index": index,
                "current_question": question
            }},
            upsert=True
        )

    def store_response(self, email, response_text, timestamp=None, question=None):
        """Store a family member's response in the database"""
        try:
            if timestamp is None:
                timestamp = datetime.utcnow()
                
            logger.info(f"Storing response from {email}")
            logger.debug(f"Response text: {response_text[:100]}...")  # Log first 100 chars
            
            # Create document with required information
            document = {
                'question_id': question.get('id'),  # Assuming questions have IDs
                'question_text': question.get('question'),
                'family_member_email': email,
                'family_member_name': self.get_family_member_name(email),  # New helper method needed
                'response_date': timestamp,
                'response_text': response_text
            }
            
            result = self.db.responses.insert_one(document)
            
            logger.info(f"Successfully stored response with ID: {result.inserted_id}")
            return result.inserted_id
            
        except Exception as e:
            logger.error(f"Failed to store response from {email}: {str(e)}")
            raise

    def get_family_member_name(self, email):
        """Get family member name from email"""
        try:
            # Look up family member in the family_members collection
            member = self.db.family_members.find_one({'email': email})
            return member['name'] if member else None
        except Exception as e:
            logger.error(f"Failed to get family member name for {email}: {str(e)}")
            return None 