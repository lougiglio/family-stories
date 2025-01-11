import os
import logging
import smtplib
import imaplib
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class HealthChecker:
    def __init__(self, app):
        """
        Initialize health checker with reference to main app
        """
        self.app = app
        self.required_files = {
            'emails.csv': False,
            'questions.csv': False,
            'config.yml': False
        }
        self.required_env_vars = [
            'EMAIL_USERNAME',
            'EMAIL_PASSWORD',
            'MONGODB_USERNAME',
            'MONGODB_PASSWORD'
        ]

    def check_health(self) -> dict:
        """Run all health checks and return detailed status"""
        checks = {
            "database": self._check_database(),
            "smtp": self._check_smtp(),
            "imap": self._check_imap(),
            "files": self._check_files(),
            "data": self._check_data_integrity(),
            "env_vars": self._check_env_vars(),
            "rate_limit": self._check_rate_limit_status()
        }
        
        is_healthy = all(checks.values())
        self._log_health_status(checks, is_healthy)
        return {
            "healthy": is_healthy,
            "checks": checks,
            "timestamp": datetime.now().isoformat()
        }

    def _check_database(self) -> bool:
        """Verify database connection and basic operations"""
        try:
            # Test database connection
            self.app.response_dao.db.admin.command('ping')
            
            # Test write operation
            test_doc = {"_id": "healthcheck", "timestamp": datetime.now()}
            self.app.response_dao.db.healthcheck.replace_one(
                {"_id": "healthcheck"},
                test_doc,
                upsert=True
            )
            
            # Test read operation
            result = self.app.response_dao.db.healthcheck.find_one({"_id": "healthcheck"})
            if not result:
                logger.error("Database read test failed")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False

    def _check_smtp(self) -> bool:
        """Verify SMTP server connection"""
        try:
            with smtplib.SMTP(self.app.email_settings['smtp_server'], 
                             self.app.email_settings['smtp_port']) as server:
                server.starttls()
                server.login(self.app.email_settings['username'], 
                           self.app.email_settings['password'])
            return True
        except Exception as e:
            logger.error(f"SMTP health check failed: {str(e)}")
            return False

    def _check_imap(self) -> bool:
        """Verify IMAP server connection"""
        try:
            with imaplib.IMAP4_SSL(self.app.email_settings['imap_server']) as imap:
                imap.login(self.app.email_settings['username'], 
                          self.app.email_settings['password'])
            return True
        except Exception as e:
            logger.error(f"IMAP health check failed: {str(e)}")
            return False

    def _check_files(self) -> bool:
        """Check existence and readability of required files"""
        for file in self.required_files:
            if os.path.exists(file):
                try:
                    with open(file, 'r') as f:
                        f.read(1)
                    self.required_files[file] = True
                except Exception as e:
                    logger.error(f"File {file} exists but is not readable: {str(e)}")
                    
        return all(self.required_files.values())

    def _check_data_integrity(self) -> bool:
        """Verify data integrity and application state"""
        try:
            if not self.app.family_members:
                logger.error("No family members loaded")
                return False
            
            if not self.app.questions:
                logger.error("No questions loaded")
                return False
            
            if not isinstance(self.app.current_question_index, int):
                logger.error("Invalid question index")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Data integrity check failed: {str(e)}")
            return False

    def _check_env_vars(self) -> bool:
        """Verify all required environment variables are set"""
        missing_vars = [var for var in self.required_env_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"Missing environment variables: {missing_vars}")
            return False
        return True

    def _log_health_status(self, checks: Dict[str, bool], is_healthy: bool) -> None:
        """Log detailed health check results"""
        logger.info("Health check results: %s", checks)
        
        if is_healthy:
            logger.info("Health check passed successfully")
        else:
            failed_checks = [k for k, v in checks.items() if not v]
            logger.error("Health check failed for: %s", failed_checks)
