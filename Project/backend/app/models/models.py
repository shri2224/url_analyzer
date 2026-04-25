from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean
from app.core.database import Base
from datetime import datetime

class AccountRegistry(Base):
    """Tracks all Gmail accounts ever connected — persists even after disconnect."""
    __tablename__ = "account_registry"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    is_connected = Column(Boolean, default=False)

class UrlScan(Base):
    __tablename__ = "url_scans"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    risk_score = Column(Integer, default=0)
    verdict = Column(String)
    full_report_json = Column(JSON) # Stores the full AnalysisReport structure

class EmailScan(Base):
    __tablename__ = "email_scans"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(String, unique=True, index=True)
    subject = Column(String)
    sender = Column(String)
    date = Column(DateTime)
    overall_verdict = Column(String)
    scan_data_json = Column(JSON) # Stores list of EmailUrl objects and other metadata
    
    # SIEM Fields
    status = Column(String, default="Open") # Open, Resolved, False Positive, Ignored
    closure_notes = Column(Text, nullable=True)
    account = Column(String, nullable=True) # The email account that received this message
    auth_results = Column(JSON, nullable=True) # Stores SPF, DKIM, DMARC results

