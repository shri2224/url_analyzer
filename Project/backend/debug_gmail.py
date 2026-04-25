import sys
import os

# Add current dir to path to import app modules
sys.path.append(os.getcwd())

from app.modules.gmail_agent import GmailAgent

def test_gmail():
    print("Initializing GmailAgent...")
    agent = GmailAgent()
    
    print(f"Creds path: {agent.creds_path}")
    print(f"Token path: {agent.token_path}")
    
    print("Authenticating...")
    auth_success = agent.authenticate()
    print(f"Auth Success: {auth_success}")
    
    if not auth_success:
        print("Authentication failed!")
        return

    print("Fetching profile...")
    profile = agent.get_profile_email()
    print(f"Profile Email: {profile}")
    
    print("Fetching recent emails...")
    emails = agent.fetch_recent_emails(limit=5)
    print(f"Fetched {len(emails)} emails.")
    
    for email in emails:
        print(f" - {email.get('subject', 'No Subject')} ({email.get('email_id')})")
        if 'urls' in email:
             print(f"   URLs: {len(email['urls'])}")

if __name__ == "__main__":
    test_gmail()
