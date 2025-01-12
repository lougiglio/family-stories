from datetime import datetime
import os
import logging
import smtplib
import imaplib

logger = logging.getLogger(__name__)

class HealthChecker:
    def __init__(self, app):
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
            return bool(result)
            
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False

    def _check_smtp(self) -> bool:
        try:
            with smtplib.SMTP(self.app.config.email_settings['smtp_server'], 
                             self.app.config.email_settings['smtp_port']) as server:
                server.starttls()
                server.login(self.app.config.email_settings['username'], 
                           self.app.config.email_settings['password'])
            return True
        except Exception as e:
            logger.error(f"SMTP health check failed: {str(e)}")
            return False

    def _check_imap(self) -> bool:
        try:
            mail = imaplib.IMAP4_SSL(self.app.config.email_settings['imap_server'])
            mail.login(self.app.config.email_settings['username'], 
                      self.app.config.email_settings['password'])
            mail.logout()
            return True
        except Exception as e:
            logger.error(f"IMAP health check failed: {str(e)}")
            return False

    def _check_files(self) -> bool:
        all_exist = True
        for filename in self.required_files:
            exists = os.path.exists(filename)
            self.required_files[filename] = exists
            if not exists:
                logger.error(f"Required file missing: {filename}")
                all_exist = False
        return all_exist

    def _check_data_integrity(self) -> bool:
        try:
            has_questions = bool(self.app.questions)
            has_family_members = bool(self.app.family_members)
            has_quotes = bool(self.app.quotes)
            
            if not all([has_questions, has_family_members, has_quotes]):
                logger.error("Data integrity check failed: Missing required data")
                return False
            return True
        except Exception as e:
            logger.error(f"Data integrity check failed: {str(e)}")
            return False

    def _check_env_vars(self) -> bool:
        missing_vars = [var for var in self.required_env_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"Missing environment variables: {missing_vars}")
            return False
        return True

    def _check_rate_limit_status(self) -> bool:
        try:
            rate_limit = self.app.config.email_settings.get('rate_limit', {})
            has_max_emails = 'max_emails_per_hour' in rate_limit
            has_delay = 'delay_between_emails' in rate_limit
            
            if not all([has_max_emails, has_delay]):
                logger.error("Rate limit configuration incomplete")
                return False
            return True
        except Exception as e:
            logger.error(f"Rate limit check failed: {str(e)}")
            return False

    def _log_health_status(self, checks: dict, is_healthy: bool):
        status = "HEALTHY" if is_healthy else "UNHEALTHY"
        logger.info(f"Health check status: {status}")
        for check, result in checks.items():
            if not result:
                logger.error(f"Health check failed: {check}")
