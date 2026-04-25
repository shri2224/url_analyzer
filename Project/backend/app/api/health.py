from fastapi import APIRouter
from app.modules.cti_checker import CTIChecker
from app.modules.reporter import Reporter
from app.modules.reporter import Reporter
import app.state as state
import os
import time

health_router = APIRouter()

@health_router.get("/health/full")
async def health_check():
    status = {
        "virustotal": {"status": "unknown", "message": ""},
        "domainduck": {"status": "unknown", "message": ""},
        "ollama": {"status": "unknown", "message": ""},
        "gmail": {"status": "unknown", "message": ""}
    }

    # 1. CTI Checks
    cti = CTIChecker()
    # Test with Google (safe)
    try:
        res = await cti.check_url("https://google.com")
        
        # VT
        vt = res.get("sources", {}).get("virustotal", {})
        if vt.get("error"):
            status["virustotal"] = {"status": "error", "message": vt["error"]}
        else:
            status["virustotal"] = {"status": "connected", "message": "OK"}

        # DomainDuck
        dd = res.get("sources", {}).get("domainduck", {})
        if dd.get("error"):
            status["domainduck"] = {"status": "error", "message": dd["error"]}
        else:
            status["domainduck"] = {"status": "connected", "message": f"Age: {dd.get('age_days', 'N/A')} days"}

    except Exception as e:
        status["virustotal"] = {"status": "error", "message": str(e)}
        status["domainduck"] = {"status": "error", "message": str(e)}

    # 2. Ollama Check
    reporter = Reporter()
    try:
        response = await reporter.client.chat(model=reporter.model_name, messages=[
            {'role': 'user', 'content': 'ping'},
        ])
        if response.message.content:
            status["ollama"] = {"status": "connected", "message": "OK"}
    except Exception as e:
        status["ollama"] = {"status": "error", "message": str(e)}

    # 3. Gmail Check (Shared State)
    email_addr = state.gmail_agent.get_profile_email()
    if email_addr:
         status["gmail"] = {"status": "connected", "message": f"Connected as {email_addr}"}
    else:
         # Fallback to token check
         token_path = "token.json" 
         if os.path.exists(token_path) or os.path.exists(os.path.join("backend", "token.json")):
             status["gmail"] = {"status": "connected", "message": "Token Found (Auth required)"}
         else:
             status["gmail"] = {"status": "disconnected", "message": "No token.json found"}

    # 4. Extension Check
    status["extension"] = {"status": "unknown", "message": "Not installed or active"}
    if state.last_extension_heartbeat:
        elapsed = time.time() - state.last_extension_heartbeat
        if elapsed < 300: # 5 minutes
             status["extension"] = {"status": "connected", "message": "Active"}
        else:
             status["extension"] = {"status": "disconnected", "message": f"Last seen {int(elapsed)}s ago"}


    return status
