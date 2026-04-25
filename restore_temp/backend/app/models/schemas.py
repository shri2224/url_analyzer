from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class UrlRequest(BaseModel):
    url: str

class RedirectionNode(BaseModel):
    step: int
    url: str
    status: int
    headers: Dict[str, str]
    ip_address: Optional[str] = None
    screenshot: Optional[str] = None  # Base64 or path
    body_summary: Optional[str] = None
    cti_data: Optional[Dict[str, Any]] = None
    extracted_links: List[str] = []
    code_analysis_verdict: Optional[str] = None
    domain_age_data: Optional[Dict[str, Any]] = None

class AnalysisReport(BaseModel):
    original_url: str
    final_url: str
    chain: List[RedirectionNode]
    summary_report: Optional[str] = None
    children: List['AnalysisReport'] = []  # For recursive analysis of extracted links

