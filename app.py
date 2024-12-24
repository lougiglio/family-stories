import smtplib
import schedule
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yaml
from email_template import EmailTemplate
import pandas as pd
from database.response_dao import ResponseDAO
import imaplib
import email

class FamilyStoriesApp:
    def __init__(self, config_file='config.yml'):
        self.current_question_index = 0
        self.load_config(config_file)
        self.questions = self.load_questions()
        self.response_dao = ResponseDAO()
        
    def load_config(self, config_file):
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
            self.email_settings = config['email']
        self.family_members = self.load_family_members()
    
    def load_family_members(self, csv_file='emails.csv'):
        try:
            df = pd.read_csv(csv_file)
            return [{'name': name, 'email': email} for name, email in zip(df['name'], df['email'])]
        except Exception as e:
            print(f"Failed to load family members: {str(e)}")
            return []
    
    def load_questions(self, csv_file='questions.csv'):
        try:
            df = pd.read_csv(csv_file)
            return df['question'].tolist()
        except Exception as e:
            print(f"Failed to load questions: {str(e)}")
            return []
    
    def send_email(self, member, question):
        msg = MIMEMultipart('alternative')
        msg['From'] = self.email_settings['username']
        msg['To'] = member['email']
        msg['Subject'] = "Weekly Family Story Question"
        
        # Get email content from template
        text, html = EmailTemplate.get_email_content(question, member['name'])
        
        # Attach both plain text and HTML versions
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        
        msg.attach(part1)
        msg.attach(part2)
        
        try:
            server = smtplib.SMTP(self.email_settings['smtp_server'], self.email_settings['smtp_port'])
            server.starttls()
            server.login(self.email_settings['username'], self.email_settings['password'])
            server.send_message(msg)
            server.quit()
            print(f"Email sent successfully to {member['email']}")
        except Exception as e:
            print(f"Failed to send email to {member['email']}: {str(e)}")

    def send_weekly_questions(self):
        if not self.questions:
            print("No questions available to send")
            return
            
        question = self.questions[self.current_question_index]
        for member in self.family_members:
            self.send_email(member, question)
        
        self.current_question_index = (self.current_question_index + 1) % len(self.questions)

    def check_email_responses(self):
        try:
            print(f"Connecting to IMAP server: {self.email_settings['imap_server']}")
            mail = imaplib.IMAP4_SSL(self.email_settings['imap_server'])
            print("Logging in...")
            mail.login(self.email_settings['username'], self.email_settings['password'])
            print("Selecting inbox...")
            mail.select('inbox')

            # Only search for replies (subject starting with "Re:")
            print("Searching for unread response messages...")
            _, messages = mail.search(None, 'UNSEEN SUBJECT "Re: Weekly Family Story Question"')
            
            message_count = len(messages[0].split())
            print(f"Found {message_count} unread responses")

            current_question = self.questions[self.current_question_index]
            
            for msg_num in messages[0].split():
                print(f"Processing message {msg_num}...")
                _, msg_data = mail.fetch(msg_num, '(RFC822)')
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                sender_email = email.utils.parseaddr(email_message['from'])[1]
                
                # Find the family member's name from our list
                sender_name = next(
                    (member['name'] for member in self.family_members 
                     if member['email'] == sender_email),
                    'Unknown'
                )
                print(f"Message from: {sender_name} ({sender_email})")

                response_text = ""
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        response_text = part.get_payload(decode=True).decode()
                        break

                print(f"Storing response from {sender_email}...")
                self.response_dao.store_response(
                    self.current_question_index,
                    sender_email,
                    response_text,
                    sender_name,
                    current_question
                )

            mail.close()
            mail.logout()
            print("Email check completed successfully")

        except Exception as e:
            print(f"Error checking email responses: {str(e)}")
            raise

def main():
    app = FamilyStoriesApp()
    
    # Schedule weekly question sending
    schedule.every().sunday.at("09:00").do(app.send_weekly_questions)
    
    # Schedule email response checking every 5 minutes
    schedule.every(5).minutes.do(app.check_email_responses)
    
    print("Family Stories App is running...")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
