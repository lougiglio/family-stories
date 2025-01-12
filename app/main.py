from app.core.app import FamilyStoriesApp
import schedule
import signal
import sys
import logging
import time

logger = logging.getLogger(__name__)

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}")
    if app:
        app.stop()

def main():
    global app
    app = FamilyStoriesApp()
    
    # Set up signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Schedule weekly question sending (Sunday at 6 AM)
        schedule.every().sunday.at("06:00").do(app.send_weekly_question)
        logger.info("Scheduled weekly questions for Sunday at 06:00")
        
        # Schedule hourly response checking
        schedule.every().hour.do(app.check_email_responses)
        logger.info("Scheduled hourly response checking")
        
        logger.info("Application started successfully")
        
        # Main loop
        while app.running:
            schedule.run_pending()
            time.sleep(60)
            
    except Exception as e:
        logger.error(f"Fatal error in main loop: {str(e)}")
        app.stop()
        sys.exit(1)
    
    logger.info("Application shutdown complete")
    sys.exit(0)

if __name__ == "__main__":
    main()
