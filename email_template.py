class EmailTemplate:
    @staticmethod
    def get_email_content(question):
        # Plain text version
        text = f"""
        Dear Family Member,
        
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
                <p style="color: #34495e;">Dear Family Member,</p>
                
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