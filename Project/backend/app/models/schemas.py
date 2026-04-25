from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class UrlRequest(BaseModel):
    url: str

class RedirectionNode(BaseModel):
    step: int
    url: str
    status: int
    headers: Dict[str, str] = {}
    screenshot: Optional[str] = None
    body_summary: Optional[str] = None
    extracted_links: List[str] = []
    cti_data: Optional[Dict[str, Any]] = None
    code_analysis_verdict: Optional[str] = None

class AnalysisReport(BaseModel):
    original_url: str
    final_url: str
    chain: List[RedirectionNode]
    summary_report: str
    children: List['AnalysisReport'] = []

class UrlScanResponse(BaseModel):
    id: int
    url: str
    timestamp: datetime
    risk_score: int
    verdict: str
    report: AnalysisReport

class EmailUrl(BaseModel):
    url: str
    status: str
    explanation: Optional[str] = None
    full_analysis: Optional[AnalysisReport] = None

class EmailScanResult(BaseModel):
    email_id: str
    subject: str
    sender: str  # mapped from 'from'
    date: str
    urls: List[EmailUrl]
    overall_verdict: str
    status: str = "Open"
    closure_notes: Optional[str] = None

class ResolutionRequest(BaseModel):
    status: str
    closure_notes: str
