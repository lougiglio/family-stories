from pymongo import MongoClient, errors
from pymongo.collection import Collection
from typing import Optional
import yaml
from pathlib import Path
import time
import logging
import os
from dotenv import load_dotenv
from pymongo.errors import ConnectionFailure

# Add logger configuration
logger = logging.getLogger(__name__)

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
        """Establish database connection with connection pooling"""
        try:
            self.client = MongoClient(
                self.db_settings['mongodb_uri'],
                maxPoolSize=50,
                waitQueueTimeoutMS=2500,
                connectTimeoutMS=2000,
                serverSelectionTimeoutMS=3000,
                retryWrites=True
            )
            self.db = self.client[self.db_settings['database_name']]
            
            # Test connection
            self.client.admin.command('ping')
            self.setup_collections()
            
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"Error connecting to database: {str(e)}")
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
        
        # Set up app_state collection and ensure question_index document exists
        if "question_index" not in self.db.app_state.find_one({"_id": "question_index"}, {"_id": 1}):
            self.db.app_state.insert_one({
                "_id": "question_index",
                "current_index": 0
            })

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
                    logging.warning(f"Connection attempt {attempt + 1} failed: {str(e)}")
                    time.sleep(self.RETRY_DELAY)
                else:
                    logging.error(f"All connection attempts failed: {str(e)}")
                    raise

    def close(self):
        """Close database connection"""
        if hasattr(self, 'client'):
            self.client.close() 

    def validate_config(self, config):
        """Validate all required configuration fields"""
        required_fields = {
            'email': {
                'smtp_server': str,
                'smtp_port': int,
                'imap_server': str,
                'username': str,
                'password': str,
                'rate_limit': dict
            },
            'database': {
                'mongodb_uri': str,
                'database_name': str
            }
        }

        def validate_section(section, requirements):
            if section not in config:
                raise ValueError(f"Missing configuration section: {section}")
            
            for field, field_type in requirements.items():
                if field not in config[section]:
                    raise ValueError(f"Missing {section}.{field} in configuration")
                if not isinstance(config[section][field], field_type):
                    raise TypeError(f"Invalid type for {section}.{field}")

        for section, requirements in required_fields.items():
            validate_section(section, requirements) 