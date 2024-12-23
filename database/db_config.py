from pymongo import MongoClient
import yaml
from pathlib import Path

class DatabaseManager:
    _instance = None

    def __new__(cls, config_file=None):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_file=None):
        if self._initialized:
            return
            
        self.load_config(config_file)
        self.connect()
        self._initialized = True

    def load_config(self, config_file):
        if config_file is None:
            config_file = Path('config.yml')
            
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
            self.db_settings = config['database']

    def connect(self):
        """Establish database connection"""
        try:
            self.client = MongoClient(self.db_settings['mongodb_uri'])
            self.db = self.client[self.db_settings['database_name']]
            
            # Create indexes
            self.db.responses.create_index([
                ("question_id", 1),
                ("family_member_email", 1),
                ("response_date", -1)
            ])
            
            print("Successfully connected to MongoDB")
        except Exception as e:
            print(f"Error connecting to database: {str(e)}")
            raise

    def close(self):
        """Close database connection"""
        if hasattr(self, 'client'):
            self.client.close() 