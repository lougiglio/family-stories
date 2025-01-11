import time
import logging
from datetime import datetime, timedelta

class EmailRateLimiter:
    def __init__(self, max_emails_per_hour, delay_between_emails):
        self.max_emails_per_hour = max_emails_per_hour
        self.delay_between_emails = delay_between_emails
        self.emails_sent = 0
        self.period_start = datetime.now()

    def wait_if_needed(self):
        """Check and wait if rate limits are reached"""
        current_time = datetime.now()
        
        # Reset counter if hour has passed
        if current_time - self.period_start > timedelta(hours=1):
            self.emails_sent = 0
            self.period_start = current_time
            return

        # Check hourly limit
        if self.emails_sent >= self.max_emails_per_hour:
            wait_seconds = 3600 - (current_time - self.period_start).total_seconds()
            if wait_seconds > 0:
                logging.info(f"Hourly rate limit reached. Waiting {wait_seconds:.2f} seconds...")
                time.sleep(wait_seconds)
                self.emails_sent = 0
                self.period_start = datetime.now()

        # Always wait the minimum delay between emails
        time.sleep(self.delay_between_emails)

    def record_email_sent(self):
        """Record that an email was sent"""
        self.emails_sent += 1 