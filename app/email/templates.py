from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

class EmailTemplate:
    @staticmethod
    def get_email_content(question, recipient_name, questioner_name, quote, quote_author):
        current_date = datetime.now().strftime('%b %Y')
        
        # Get the absolute path to the templates directory
        template_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'email_templates')
        template_path = os.path.join(template_dir, 'weekly_question.html')
        
        # Plain text version
        text = f"""
        This week, {questioner_name} would like you to answer the following question:

        {current_date}

        Good morning, {recipient_name}!
        This week, {questioner_name} would like you to answer the following question:

        {question}

        "{quote}" - {quote_author}

        Instructions
        In 150 or more words reply to this email with your answer to this question. 
        When we receive your story, we'll automatically save it in your private account 
        to be accessed later by you or family members.
        """
        
        # HTML version
        try:
            with open(template_path, 'r') as f:
                html_template = f.read()
                
            # Replace placeholders
            replacements = {
                '{{recipient_name}}': recipient_name,
                '{{question}}': question,
                '{{questioner_name}}': questioner_name,
                '{{quote}}': quote,
                '{{quote_author}}': quote_author,
                '{{issue_date}}': current_date
            }
            
            html = html_template
            for key, value in replacements.items():
                html = html.replace(key, value)
                
        except Exception as e:
            logger.error(f"Error loading HTML template: {str(e)}")
            html = text  # Fallback to plain text if HTML template fails
        
        return text.strip(), html

    @staticmethod
    def get_confirmation_email_content(name, question):
        text = f"""
        Dear {name},

        Thank you for sharing your story in response to the question:
        "{question}"

        Your response has been safely stored and can be accessed by you 
        and your family members through your private account.

        Best regards,
        Family Stories Team
        """
        
        # Simple HTML version (you might want to create a proper template file)
        html = f"""
        <html>
            <body>
                <p>Dear {name},</p>
                <p>Thank you for sharing your story in response to the question:</p>
                <p><em>"{question}"</em></p>
                <p>Your response has been safely stored and can be accessed by you 
                and your family members through your private account.</p>
                <p>Best regards,<br>Family Stories Team</p>
            </body>
        </html>
        """
        
        return text.strip(), html
