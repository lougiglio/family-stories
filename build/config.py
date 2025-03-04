import yaml
import os
import pandas as pd
from dotenv import load_dotenv
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class Config:
    def __init__(self, config_file='build/config.yml'):
        env_path = Path(__file__).parent.parent / '.env'
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
        else:
            logger.warning(f".env file not found at {env_path}. Environment variables must be set manually.")
        
        self._validate_environment()
        self.load_config(config_file)

    def _validate_environment(self):
        required_vars = [
            'EMAIL_USERNAME', 
            'EMAIL_PASSWORD', 
            'MONGODB_USERNAME', 
            'MONGODB_PASSWORD',
            'MONGODB_HOST',
            'MONGODB_PORT'
        ]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise EnvironmentError(f"Missing required environment variables: {missing_vars}")

    def load_config(self, config_file):
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
            email_settings = config.get('email', {})
            
            # Replace email credential placeholders
            email_settings['username'] = os.getenv('EMAIL_USERNAME')
            email_settings['password'] = os.getenv('EMAIL_PASSWORD')
            
            # Debug log
            logger.debug(f"Loaded email settings - SMTP: {email_settings['smtp_server']}:{email_settings['smtp_port']}, Username: {email_settings['username']}")
            
            self.email_settings = email_settings
            
            # Construct MongoDB URI with environment variables
            mongodb_username = os.getenv('MONGODB_USERNAME')
            mongodb_password = os.getenv('MONGODB_PASSWORD')
            mongodb_host = os.getenv('MONGODB_HOST', 'localhost')
            mongodb_port = os.getenv('MONGODB_PORT', '27017')
            
            # Construct MongoDB URI with authSource
            self.db_settings = {
                'mongodb_uri': f"mongodb://{mongodb_username}:{mongodb_password}@{mongodb_host}:{mongodb_port}/family_stories?authSource=admin",
                'database_name': 'family_stories'
            }
            
            self._validate_config()

    def _validate_config(self):
        required_settings = {
            'smtp_server': str,
            'smtp_port': int,
            'imap_server': str,
            'username': str,
            'password': str
        }
        
        for setting, expected_type in required_settings.items():
            if setting not in self.email_settings:
                raise ValueError(f"Missing required email setting: {setting}")
            if not isinstance(self.email_settings[setting], expected_type):
                raise TypeError(f"Invalid type for {setting}")

    def load_family_members(self, csv_file='assets/emails.csv'):
        try:
            file_path = os.path.join(os.getcwd(), csv_file)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"CSV file not found: {file_path}")
            df = pd.read_csv(file_path)
            
            members = []
            for _, row in df.iterrows():
                member = {'name': row['Name'], 'email': row['Email']}
                
                # Check for ReceiveForwards column
                if 'ReceiveForwards' in df.columns:
                    member['receive_forwards'] = bool(row['ReceiveForwards'])
                else:
                    member['receive_forwards'] = True
                
                # Check for ReceiveQuestions column
                if 'ReceiveQuestions' in df.columns:
                    member['receive_questions'] = bool(row['ReceiveQuestions'])
                else:
                    member['receive_questions'] = True
                
                members.append(member)
            
            return members
        except Exception as e:
            logger.error(f"Failed to load family members: {str(e)}")
            return []

    def load_questions(self, csv_file='assets/questions.csv'):
        try:
            file_path = os.path.join(os.getcwd(), csv_file)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"CSV file not found: {file_path}")
            df = pd.read_csv(file_path)
            return [{'question': row['Question'], 'questioner': row['Questioner']} 
                   for _, row in df.iterrows()]
        except Exception as e:
            logger.error(f"Failed to load questions: {str(e)}")
            return []

    def load_quotes(self, csv_file='assets/quotes.csv'):
        try:
            file_path = os.path.join(os.getcwd(), csv_file)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"CSV file not found: {file_path}")
            df = pd.read_csv(file_path)
            return [{'quote': row['Quote'], 'author': row['Author']} 
                   for _, row in df.iterrows()]
        except Exception as e:
            logger.error(f"Failed to load quotes: {str(e)}")
            return []

    def load_forwarding_list(self, csv_file='assets/forwarding_list.csv'):
        """Load the list of email addresses to forward responses to"""
        try:
            file_path = os.path.join(os.getcwd(), csv_file)
            if not os.path.exists(file_path):
                logger.warning(f"Forwarding list file not found: {file_path}. Using family members list instead.")
                return None
                
            df = pd.read_csv(file_path)
            return [{'name': row['Name'], 'email': row['Email']} 
                   for _, row in df.iterrows() if row['Email'].strip()]
        except Exception as e:
            logger.error(f"Failed to load forwarding list: {str(e)}")
            return None
