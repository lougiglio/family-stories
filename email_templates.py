class EmailTemplate:
    @staticmethod
    def get_email_content(question, recipient_name):
        # Plain text version
        text = f"""
        Dear {recipient_name},
        
        This week's question is:
        
        {question}
        
        Please reply to this email with your story. Your memories are precious to us!
        
        With love,
        Your Family
        """
        
        # HTML version
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">Weekly Family Story</h2>
                <p style="color: #34495e;">Dear {recipient_name},</p>
                
                <div style="background-color: #f7f9fc; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <p style="font-style: italic; color: #7f8c8d;">This week's question is:</p>
                    <h3 style="color: #2980b9;">{question}</h3>
                </div>
                
                <p style="color: #34495e;">Please reply to this email with your story. Your memories are precious to us!</p>
                
                <p style="color: #34495e; margin-top: 30px;">With love,<br>Your Family</p>
            </body>
        </html>
        """
        
        return text, html 

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