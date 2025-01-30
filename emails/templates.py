from datetime import datetime
import os
import logging
from pathlib import Path
import re

logger = logging.getLogger(__name__)

class WeeklyQuestionEmail:
    @staticmethod
    def get_content(question, recipient_name, questioner_name, quote, quote_author, question_number=None):
        current_date = datetime.now().strftime('%b %Y')
        
        # If question_number is not provided, try to get it from the question object
        if question_number is None and isinstance(question, dict):
            question_number = question.get('id', 1)
        elif question_number is None:
            question_number = 1
            
        issue_number = f"#{question_number:02d}"  # Format as 2 digits with leading zero
        issue_date = datetime.now().strftime('%B %d, %Y')
        
        template_path = os.path.join(os.path.dirname(__file__), 'templates/weekly_question.html')
        logger.debug(f"Template path: {template_path}")
        
        try:
            with open(template_path, 'r', encoding='utf-8') as file:
                html_template = file.read()
                
            # Replace text placeholders
            html = html_template.replace('{{recipient_name}}', recipient_name)
            html = html.replace('{{questioner_name}}', questioner_name)
            html = html.replace('{{question}}', question)
            html = html.replace('{{quote}}', quote)
            html = html.replace('{{quote_author}}', quote_author)
            html = html.replace('{{issue_number}}', issue_number)
            html = html.replace('{{issue_date}}', issue_date)
            
            # Add Content-Type meta tag if not present
            if '<meta http-equiv="Content-Type"' not in html:
                head_end = '</head>'
                meta_tag = '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">\n'
                html = html.replace(head_end, meta_tag + head_end)
            
            return html
            
        except Exception as e:
            logger.error(f"Failed to load weekly question template: {str(e)}")
            # Fall back to basic HTML template
            return f"""
            <html>
                <head>
                    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                </head>
                <body>
                    <p>Good morning, {recipient_name}!</p>
                    <p>This week, {questioner_name} would like you to answer the following question:</p>
                    <p><strong>{question}</strong></p>
                    <p>"{quote}" - {quote_author}</p>
                    <p>Instructions: In 150 or more words reply to this email with your answer to this question. 
                    When we receive your story, we'll automatically save it in your private account 
                    to be accessed later by you or family members.</p>
                    <p><em>{current_date}</em></p>
                </body>
            </html>
            """

class ConfirmationEmail:
    @staticmethod
    def get_content(recipient_name, question):
        template_path = os.path.join(os.path.dirname(__file__), 'templates/confirmation_email.html')
        logger.debug(f"Confirmation template path: {template_path}")
        
        try:
            with open(template_path, 'r', encoding='utf-8') as file:
                html = file.read()
                
            # Replace content placeholders
            current_date = datetime.now().strftime('%b %Y')
            html = html.replace('Jan 2025', current_date)
            
            # Update message content
            html = html.replace('Welcome to Family History', 'Thank You for Sharing')
            html = html.replace('Thanks for signing up!', f'Response Received: "{question}"')
            html = html.replace('Confirm your subscription', 'Your story has been saved')
            html = html.replace('<a href="#insertUrlLink"', '<a href="#"')  # Remove subscription link functionality
            html = html.replace('Yes, I want to subscribe', 'View Your Stories')
            
            # Update footer text
            footer_text = """If you have any questions about your stored stories or need assistance accessing them, 
                            you can reply to this email or contact us at familyhistory@mail.com."""
            html = re.sub(r'If you didn\'t subscribe.*?familyhistory@mail\.com\.', 
                         footer_text, 
                         html, 
                         flags=re.DOTALL)
            
            return html
            
        except Exception as e:
            logger.error(f"Failed to load confirmation template: {str(e)}")
            # Fall back to basic text template
            return f"""
            <html>
                <head>
                    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                </head>
                <body>
                    <p>Dear {recipient_name},</p>
                    <p>Thank you for sharing your story in response to the question:</p>
                    <p>"{question}"</p>
                    <p>Your response has been safely stored and can be accessed by you 
                    and your family members through your private account.</p>
                    <p>Best regards,<br>Family Stories Team</p>
                </body>
            </html>
            """
