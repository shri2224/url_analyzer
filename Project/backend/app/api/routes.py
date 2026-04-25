from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Depends
from sqlalchemy.orm import Session
from typing import List

from app.models import schemas
from app.models import models
from app.modules.browser_agent import BrowserAgent
from app.modules.cti_checker import CTIChecker
from app.modules.reporter import Reporter
import app.state as state
from app.core.database import get_db, engine
from app.core import crud
import time
import traceback
import asyncio

# Create tables if they don't exist
models.Base.metadata.create_all(bind=engine)

router = APIRouter()

# Initialize modules
browser_agent = BrowserAgent()
cti_checker = CTIChecker()
reporter = Reporter()

@router.post("/analyze", response_model=schemas.AnalysisReport)
async def analyze_url(request: schemas.UrlRequest, db: Session = Depends(get_db)):
    try:
        # Configuration for recursion
        MAX_DEPTH = 1
        MAX_LINKS_PER_PAGE = 3
        
        # DFS/BFS Helper
        async def process_url(url: str, depth: int) -> schemas.AnalysisReport:
            print(f"Analyzing: {url} (Depth: {depth})")
            
            # 1. Trace
            chain = await browser_agent.trace(url)
            
            # 2. Enrich Nodes (Parallel CTI)
            if chain:
                # 2a. Gather all CTI checks concurrently
                cti_tasks = [cti_checker.check_url(node.url) for node in chain]
                cti_results = await asyncio.gather(*cti_tasks)
                
                # 2b. Assign results and run local analysis
                for i, node in enumerate(chain):
                    node.cti_data = cti_results[i]
                    
                    # Code Analysis + Dataset Scan
                    if node.body_summary:
                        node.code_analysis_verdict = await reporter.analyze_code(node.body_summary, node.headers)
                        
                        scan_result = reporter.scan_threats(node.body_summary)
                        node.cti_data["dataset_scan"] = {
                            "match_count": scan_result["match_count"],
                            "verdict": scan_result["verdict"],
                            "matches": [
                                {"id": m["id"], "type": m["type"], "category": m["category"]}
                                for m in scan_result["matches"]
                            ]
                        }
                        
                        if scan_result["verdict"] == "Malicious" and node.cti_data.get("verdict") != "Malicious":
                            node.cti_data["verdict"] = "Malicious"
                            node.cti_data["score"] = max(node.cti_data.get("score", 0), 70)
                        elif scan_result["verdict"] == "Suspicious" and node.cti_data.get("verdict") == "Clean":
                            node.cti_data["verdict"] = "Suspicious"
                            node.cti_data["score"] = max(node.cti_data.get("score", 0), 50)

            final_node = chain[-1] if chain else None
            final_url = final_node.url if final_node else url
            
            # 3. Recursion
            children_reports = []
            if depth < MAX_DEPTH and final_node and final_node.extracted_links:
                links_to_visit = final_node.extracted_links[:MAX_LINKS_PER_PAGE]
                for link in links_to_visit:
                    if link.startswith("http"):
                        child_report = await process_url(link, depth + 1)
                        children_reports.append(child_report)

            # 4. Generate Summary
            summary = await reporter.generate_report(chain)
            
            return schemas.AnalysisReport(
                original_url=url,
                final_url=final_url,
                chain=chain,
                summary_report=summary,
                children=children_reports
            )

        # Start Analysis
        report = await process_url(request.url, 0)
        
        # Save to DB history automatically
        crud.create_url_scan(db, report)
        
        return report

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# --- HISTORY ENDPOINTS ---

@router.get("/history", response_model=List[schemas.UrlScanResponse])
def get_history(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    scans = crud.get_url_scans(db, skip=skip, limit=limit)
    # Map DB model to response schema manual if needed, but simple attribute mapping works
    return [
        schemas.UrlScanResponse(
            id=scan.id,
            url=scan.url,
            timestamp=scan.timestamp,
            risk_score=scan.risk_score,
            verdict=scan.verdict,
            report=schemas.AnalysisReport.model_validate(scan.full_report_json)  # Handles nested objects correctly
        )
        for scan in scans
    ]

@router.delete("/history/{scan_id}")
def delete_history_entry(scan_id: int, db: Session = Depends(get_db)):
    success = crud.delete_url_scan(db, scan_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"status": "deleted"}

@router.delete("/history")
def clear_history(db: Session = Depends(get_db)):
    crud.delete_all_url_scans(db)
    return {"status": "cleared"}

# --- GMAIL ENDPOINTS ---

@router.post("/gmail/scan")
async def scan_gmail(background_tasks: BackgroundTasks):
    background_tasks.add_task(state.gmail_agent.scan_emails_background, browser_agent, cti_checker, reporter)
    return {"message": "Background scan initiated", "status": "processing"}

@router.get("/gmail/results")
async def get_gmail_results(db: Session = Depends(get_db)):
    # Fetch from DB instead of memory
    scans = crud.get_email_scans(db)
    # Convert back to schema list
    results = []
    for s in scans:
        try:
            data = s.scan_data_json
            # Enrich with DB status
            data['status'] = s.status
            data['closure_notes'] = s.closure_notes
            # Always use the DB account column (authoritative source),
            # falling back to whatever is in the JSON blob
            if s.account:
                data['account'] = s.account
            data['auth_results'] = s.auth_results
            results.append(data)
        except:
            pass
    return results

@router.post("/gmail/resolve/{email_id}")
async def resolve_email_alert(email_id: str, req: schemas.ResolutionRequest, db: Session = Depends(get_db)):
    updated = crud.update_email_status(db, email_id, req.status, req.closure_notes)
    if not updated:
        raise HTTPException(status_code=404, detail="Email offense not found")
    return {"status": "updated", "new_status": updated.status}

@router.get("/gmail/status")
async def get_gmail_status(db: Session = Depends(get_db)):
    connected = state.gmail_agent.check_connection()
    email = state.gmail_agent.get_profile_email() if connected else None
    # Always upsert the registry so we track connected/disconnected state
    if email:
        crud.upsert_account_registry(db, email, is_connected=True)
    else:
        # Mark all as disconnected if we can't connect
        all_accounts = crud.get_account_registry(db)
        for acc in all_accounts:
            if acc.is_connected:
                crud.upsert_account_registry(db, acc.email, is_connected=False)
    return {"connected": connected, "email": email}

@router.get("/gmail/accounts")
async def get_gmail_accounts(db: Session = Depends(get_db)):
    """Returns all known Gmail accounts with their connection status."""
    accounts = crud.get_account_registry(db)
    return [
        {
            "email": a.email,
            "is_connected": a.is_connected,
            "first_seen": a.first_seen.isoformat() if a.first_seen else None,
            "last_seen": a.last_seen.isoformat() if a.last_seen else None,
        }
        for a in accounts
    ]


@router.get("/gmail/check-email")
async def check_email(
    subject: str = Query(..., description="Email subject line"),
    sender: str = Query("", description="Email sender address or name"),
    db: Session = Depends(get_db)
):
    subject_lower = subject.strip().lower()
    sender_lower = sender.strip().lower()
    
    # Inefficient linear scan, but consistent with previous memory logic
    # Ideally should user verify filtering in DB
    # Fetch all recent scans
    all_scans = crud.get_email_scans(db, limit=100)
    
    for scan in all_scans:
        email = scan.scan_data_json
        email_subject = email.get("subject", "").strip().lower()
        email_sender = email.get("from", "").strip().lower()
        
        if email_subject == subject_lower and (not sender_lower or sender_lower in email_sender):
            unsafe_urls = [
                {
                    "url": u.get("url", ""),
                    "status": u.get("status", "unknown"),
                    "explanation": u.get("explanation", "")
                }
                for u in email.get("urls", [])
                if u.get("status") == "unsafe"
            ]
            return {
                "found": True,
                "email_id": email.get("email_id", ""),
                "overall_verdict": email.get("overall_verdict", "unknown"),
                "subject": email.get("subject", ""),
                "sender": email.get("from", ""),
                "total_urls": len(email.get("urls", [])),
                "unsafe_urls": unsafe_urls,
                "unsafe_count": len(unsafe_urls)
            }
    
    return {"found": False, "overall_verdict": "unknown"}

@router.post("/extension/heartbeat")
async def extension_heartbeat():
    state.last_extension_heartbeat = time.time()
    return {"status": "ok", "timestamp": state.last_extension_heartbeat}
