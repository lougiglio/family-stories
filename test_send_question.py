from app import FamilyStoriesApp
import time

def test_send_first_question():
    print("Initializing FamilyStoriesApp...")
    app = FamilyStoriesApp()
    app.family_members = app.load_family_members('emails.csv')
    
    print("\nChecking loaded configuration:")
    print(f"Email settings: {app.email_settings}")
    
    print("\nChecking loaded family members:")
    print(f"Family members: {app.family_members}")
    
    print("\nChecking loaded questions:")
    print(f"Questions available: {len(app.questions)}")
    if app.questions:
        print(f"First question: {app.questions[0]}")
    
    print("\nAttempting to send first question...")
    app.send_weekly_questions()
    
    # Add delay to allow time for responses
    wait_time = 60  # 1 minute for testing
    print(f"\nWaiting {wait_time} seconds for responses...")
    
    # Check multiple times
    check_intervals = 6  # Check 6 times
    for i in range(check_intervals):
        print(f"\nCheck attempt {i+1}/{check_intervals}")
        print("Checking for email responses...")
        try:
            app.check_email_responses()
            
            # Print stored responses
            responses = app.response_dao.get_responses_by_question(app.current_question_index)
            print(f"Collected responses: {len(responses)}")
            for response in responses:
                print(f"Response from {response['family_member_email']}: {response['response_text'][:100]}...")
        except Exception as e:
            print(f"Error during check: {str(e)}")
        
        if i < check_intervals - 1:  # Don't sleep after the last check
            time.sleep(wait_time // check_intervals)
    
    print("Done!")

if __name__ == "__main__":
    test_send_first_question() 