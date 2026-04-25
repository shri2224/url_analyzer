import sys
import os
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models import models

def check_db():
    db = SessionLocal()
    try:
        count = db.query(models.EmailScan).count()
        print(f"Total Email Scans in DB: {count}")
        
        scans = db.query(models.EmailScan).order_by(models.EmailScan.date.desc()).limit(5).all()
        for scan in scans:
            print(f"- {scan.subject} ({scan.date}) [Status: {scan.status}]")
    finally:
        db.close()

if __name__ == "__main__":
    check_db()
