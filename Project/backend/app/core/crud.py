from sqlalchemy.orm import Session
from datetime import datetime
from app.models import models
from app.models import schemas
import json
from datetime import datetime

# --- URL SCANS ---

def create_url_scan(db: Session, report: schemas.AnalysisReport):
    # Calculate risk score from the final node or summary (simplified logic)
    # In reality, this might come from the report itself if it had a top-level score
    risk_score = 0
    verdict = "Clean"
    
    if report.chain:
        final_node = report.chain[-1]
        if final_node.cti_data:
            risk_score = final_node.cti_data.get("score", 0)
            verdict = final_node.cti_data.get("verdict", "Unknown")

    # Serialize pydantic model to dict for JSON storage
    report_dict = report.model_dump()

    db_scan = models.UrlScan(
        url=report.original_url,
        timestamp=datetime.utcnow(),
        risk_score=risk_score,
        verdict=verdict,
        full_report_json=report_dict
    )
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)
    
    # Auto-prune old entries (keep last 100)
    # This is a simple implementation; for high volume, use a separate cleanup task
    count = db.query(models.UrlScan).count()
    if count > 100:
        # Delete oldest
        oldest = db.query(models.UrlScan).order_by(models.UrlScan.timestamp.asc()).first()
        if oldest:
            db.delete(oldest)
            db.commit()
            
    return db_scan

def get_url_scans(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.UrlScan).order_by(models.UrlScan.timestamp.desc()).offset(skip).limit(limit).all()

def delete_url_scan(db: Session, scan_id: int):
    db_scan = db.query(models.UrlScan).filter(models.UrlScan.id == scan_id).first()
    if db_scan:
        db.delete(db_scan)
        db.commit()
        return True
    return False

def delete_all_url_scans(db: Session):
    db.query(models.UrlScan).delete()
    db.commit()

# --- EMAIL SCANS ---

def create_email_scan(db: Session, email_data: dict):
    # Check if exists
    existing = db.query(models.EmailScan).filter(models.EmailScan.email_id == email_data['email_id']).first()
    if existing:
        return existing
        
    # Parse date
    try:
        dt = datetime.fromisoformat(email_data['date'].replace('Z', '+00:00'))
    except:
        dt = datetime.utcnow()

    db_email = models.EmailScan(
        email_id=email_data['email_id'],
        subject=email_data['subject'],
        sender=email_data['from'], # mapped from 'from' to 'sender'
        date=dt,
        overall_verdict=email_data['overall_verdict'],
        scan_data_json=email_data,
        status="Open" if email_data['overall_verdict'] != 'safe' else "Closed",
        account=email_data.get('account'),
        auth_results=email_data.get('auth_results')
    )
    db.add(db_email)
    db.commit()
    db.refresh(db_email)
    return db_email

def get_email_scans(db: Session, limit: int = 100):
    return db.query(models.EmailScan).order_by(models.EmailScan.date.desc()).limit(limit).all()

def get_email_scan_by_id(db: Session, email_id: str):
    return db.query(models.EmailScan).filter(models.EmailScan.email_id == email_id).first()

def update_email_status(db: Session, email_id: str, status: str, notes: str = None):
    db_email = db.query(models.EmailScan).filter(models.EmailScan.email_id == email_id).first()
    if db_email:
        db_email.status = status
        if notes:
            db_email.closure_notes = notes
        db.commit()
        return db_email
    return None

# --- ACCOUNT REGISTRY ---

def upsert_account_registry(db: Session, email: str, is_connected: bool):
    """Insert or update an account in the registry. Never deletes — preserves disconnected state."""
    existing = db.query(models.AccountRegistry).filter(models.AccountRegistry.email == email).first()
    now = datetime.utcnow()
    if existing:
        existing.is_connected = is_connected
        existing.last_seen = now
    else:
        existing = models.AccountRegistry(
            email=email,
            is_connected=is_connected,
            first_seen=now,
            last_seen=now
        )
        db.add(existing)
    db.commit()
    db.refresh(existing)
    return existing

def get_account_registry(db: Session):
    """Return all known accounts, connected first."""
    return db.query(models.AccountRegistry).order_by(
        models.AccountRegistry.is_connected.desc(),
        models.AccountRegistry.last_seen.desc()
    ).all()

def mark_all_disconnected(db: Session):
    """Mark all accounts as disconnected (called on startup before re-checking)."""
    db.query(models.AccountRegistry).update({models.AccountRegistry.is_connected: False})
    db.commit()
