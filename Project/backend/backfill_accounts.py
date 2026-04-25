from app.core.database import SessionLocal
from app.models import models
from app.modules.gmail_agent import GmailAgent

def backfill():
    # 1. Get current authenticated email
    agent = GmailAgent()
    current_email = agent.get_profile_email()
    
    if not current_email:
        print("Could not retrieve authenticated email. Ensure credentials are valid.")
        return

    print(f"Authenticated as: {current_email}")

    # 2. Update DB
    db = SessionLocal()
    try:
        # Find records with no account
        scans = db.query(models.EmailScan).filter(
            (models.EmailScan.account == None) | (models.EmailScan.account == "Unknown")
        ).all()
        
        print(f"Found {len(scans)} records to update.")
        
        for scan in scans:
            scan.account = current_email
        
        db.commit()
        print("Backfill complete.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    backfill()
