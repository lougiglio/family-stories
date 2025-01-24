import re
import logging
import time
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionError, OperationFailure

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
            # Hide password in logs
            safe_uri = self.db_settings['mongodb_uri'].replace(
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
            
        except ConnectionError as e:
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
        # Set up responses collection
        self.db.responses.create_index([
            ("question_id", 1),
            ("family_member_email", 1),
            ("family_member_name", 1),
            ("response_date", -1)
        ])
        
        # Set up app_state collection
        if "question_index" not in self.db.app_state.find_one({"_id": "question_index"}, {"_id": 1}):
            self.db.app_state.insert_one({
                "_id": "question_index",
                "current_index": 0
            })

    def close(self):
        """Close database connection"""
        if hasattr(self, 'client'):
            self.client.close() 