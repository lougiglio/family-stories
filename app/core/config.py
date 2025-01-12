import yaml
import os
import pandas as pd
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class Config:
    def __init__(self, config_file='config.yml'):
        load_dotenv()
        self._validate_environment()
        self.load_config(config_file)

    def _validate_environment(self):
        required_vars = ['EMAIL_USERNAME', 'EMAIL_PASSWORD', 'MONGODB_USERNAME', 'MONGODB_PASSWORD']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise EnvironmentError(f"Missing required environment variables: {missing_vars}")

    def load_config(self, config_file):
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
            self.email_settings = config.get('email', {})
            
            # Construct MongoDB URI with environment variables
            mongodb_username = os.getenv('MONGODB_USERNAME')
            mongodb_password = os.getenv('MONGODB_PASSWORD')
            base_uri = config.get('database', {}).get('mongodb_uri', '')
            
            if not base_uri:
                raise ValueError("MongoDB URI not found in config")
            
            # Replace placeholders with actual values
            self.db_settings = {
                'mongodb_uri': base_uri.replace('${MONGODB_USERNAME}', mongodb_username)
                                     .replace('${MONGODB_PASSWORD}', mongodb_password),
                'database_name': config.get('database', {}).get('database_name', 'app')
            }
            
            self._validate_config()

    def _validate_config(self):
        required_settings = {
            'smtp_server': str,
            'smtp_port': int,
            'imap_server': str,
            'username': str,
            'password': str,
            'rate_limit': dict
        }
        
        for setting, expected_type in required_settings.items():
            if setting not in self.email_settings:
                raise ValueError(f"Missing required email setting: {setting}")
            if not isinstance(self.email_settings[setting], expected_type):
                raise TypeError(f"Invalid type for {setting}")

    def load_family_members(self, csv_file='emails.csv'):
        try:
            file_path = os.path.join(os.path.dirname(__file__), '..', '..', csv_file)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"CSV file not found: {file_path}")
            df = pd.read_csv(file_path)
            return [{'name': name, 'email': email} 
                   for name, email in zip(df['name'], df['email'])]
        except Exception as e:
            logger.error(f"Failed to load family members: {str(e)}")
            return []

    def load_questions(self, csv_file='questions.csv'):
        try:
            df = pd.read_csv(csv_file)
            return [{'question': row['Question'], 'questioner': row['Questioner']} 
                   for _, row in df.iterrows()]
        except Exception as e:
            logger.error(f"Failed to load questions: {str(e)}")
            return []

    def load_quotes(self, csv_file='quotes.csv'):
        try:
            df = pd.read_csv(csv_file)
            return [{'quote': row['Quote'], 'author': row['Author']} 
                   for _, row in df.iterrows()]
        except Exception as e:
            logger.error(f"Failed to load quotes: {str(e)}")
            return []
