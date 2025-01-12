from datetime import datetime

class EmailTemplate:
    @staticmethod
    def get_email_content(question, recipient_name, questioner_name, quote, quote_author):
        # Get current date and format it
        current_date = datetime.now().strftime('%b %Y')
        
        # Plain text version
        text = f"""
        This week, {questioner_name} would like you to answer the following question:

        {current_date}

        Good morning, {recipient_name}!
        This week, {questioner_name} would like you to answer the following question:

        {question}

        "{quote}" - {quote_author}

        Instructions
        In 150 or more words reply to this email with your answer to this question. When we receive your story, we'll automatically save it in your private account to be accessed later by you or family members.
        """
        
        # HTML version - using your provided template
        with open('email_templates/weekly_question.html', 'r') as f:
            html_template = f.read()
            
        # Replace placeholders in the HTML template
        html = html_template.replace('{{recipient_name}}', recipient_name)
        html = html.replace('{{question}}', question)
        html = html.replace('{{questioner_name}}', questioner_name)
        html = html.replace('{{quote}}', quote)
        html = html.replace('{{quote_author}}', quote_author)
        html = html.replace('{{issue_date}}', current_date)
        
        return text.strip(), html

    @staticmethod
    def get_confirmation_email_content(recipient_name, question):
        # Plain text version
        text = f"""
        Dear {recipient_name},

        Thank you for sharing your story! We have successfully received and stored your response to the question:

        "{question}"

        Your memories are valuable to our family history.

        Best regards,
        Family Stories App
        """
        
        # HTML version
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">Response Received</h2>
                <p style="color: #34495e;">Dear {recipient_name},</p>
                
                <p style="color: #34495e;">Thank you for sharing your story! We have successfully received and stored your response to the question:</p>
                
                <div style="background-color: #f7f9fc; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <p style="font-style: italic; color: #2980b9;">"{question}"</p>
                </div>
                
                <p style="color: #34495e;">Your memories are valuable to our family history.</p>
                
                <p style="color: #34495e; margin-top: 30px;">Best regards,<br>Family Stories App</p>
            </body>
        </html>
        """
        
        return text, html 