from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import yaml
from pathlib import Path
import time
import logging
import os
from dotenv import load_dotenv

class DatabaseManager:
    _instance = None
    MAX_RETRIES = 3
    RETRY_DELAY = 5  # seconds

    def __new__(cls, config_file=None):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_file=None):
        if self._initialized:
            return
            
        self.load_config(config_file)
        self.connect_with_retry()
        self._initialized = True

    def load_config(self, config_file):
        if config_file is None:
            config_file = Path('config.yml')
        
        # Load environment variables
        load_dotenv()
        
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
            mongodb_uri = config['database']['mongodb_uri']
            
            # Replace environment variables in the URI
            mongodb_uri = mongodb_uri.replace(
                '${MONGODB_USERNAME}', 
                os.getenv('MONGODB_USERNAME', '')
            )
            mongodb_uri = mongodb_uri.replace(
                '${MONGODB_PASSWORD}', 
                os.getenv('MONGODB_PASSWORD', '')
            )
            
            self.db_settings = config['database']
            self.db_settings['mongodb_uri'] = mongodb_uri

    def connect(self):
        """Establish database connection"""
        try:
            self.client = MongoClient(self.db_settings['mongodb_uri'])
            self.db = self.client[self.db_settings['database_name']]
            
            # Updated indexes
            self.db.responses.create_index([
                ("question_id", 1),
                ("family_member_email", 1),
                ("family_member_name", 1),
                ("response_date", -1)
            ])
            
            print("Successfully connected to MongoDB")
        except Exception as e:
            print(f"Error connecting to database: {str(e)}")
            raise

    def connect_with_retry(self):
        """Establish database connection with retry logic"""
        for attempt in range(self.MAX_RETRIES):
            try:
                self.connect()
                # Test the connection
                self.client.admin.command('ping')
                logging.info("Successfully connected to MongoDB at %s", 
                           self.db_settings['mongodb_uri'])
                return
            except ConnectionFailure as e:
                if attempt < self.MAX_RETRIES - 1:
                    logging.warning("Connection attempt %d failed. Retrying in %d seconds...", 
                                  attempt + 1, self.RETRY_DELAY)
                    time.sleep(self.RETRY_DELAY)
                else:
                    logging.error("Failed to connect to MongoDB after %d attempts", 
                                self.MAX_RETRIES)
                    raise

    def close(self):
        """Close database connection"""
        if hasattr(self, 'client'):
            self.client.close() 