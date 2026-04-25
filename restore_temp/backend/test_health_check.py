import asyncio
import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.modules.cti_checker import CTIChecker
from app.modules.reporter import Reporter
from app.core.config import OLLAMA_API_URL, OLLAMA_MODEL

async def check_services():
    print("=== Starting Backend Health Check ===\n")

    # 1. Check CTI Services
    print("--- 1. Testing CTI Services (VirusTotal & DomainDuck) ---")
    cti_checker = CTIChecker()
    test_url = "https://google.com" # Safe URL
    print(f"Checking URL: {test_url}")
    
    try:
        results = await cti_checker.check_url(test_url)
        
        # VirusTotal
        vt = results.get('sources', {}).get('virustotal', {})
        if vt.get('error'):
            print(f"❌ VirusTotal: Error - {vt['error']}")
        elif vt.get('status') == 'not_found':
             print(f"⚠️ VirusTotal: URL not found (might be expected for fresh URLs)")
        else:
            print(f"✅ VirusTotal: Connected. Stats: {vt.get('stats', 'N/A')}")

        # DomainDuck
        dd = results.get('sources', {}).get('domainduck', {})
        if dd.get('error'):
             print(f"❌ DomainDuck: Error - {dd['error']}")
        else:
             print(f"✅ DomainDuck: Connected. Age: {dd.get('age_days')} days. Report: {dd.get('raw_data', {}).get('domain', 'Unknown')}")

    except Exception as e:
        print(f"❌ CTI Check Failed: {e}")

    print("\n")

    # 2. Check Ollama / AI
    print("--- 2. Testing AI Service (Ollama) ---")
    print(f"Configured URL: {OLLAMA_API_URL}")
    print(f"Configured Model: {OLLAMA_MODEL}")
    
    reporter = Reporter()
    try:
        # Simple ping/chat
        response = await reporter.client.chat(model=reporter.model_name, messages=[
            {'role': 'user', 'content': 'Say "Hello, World!" if you are working.'},
        ])
        content = response['message']['content']
        print(f"✅ Ollama: Connected. Response: {content}")
    except Exception as e:
        print(f"❌ Ollama: Failed - {e}")

    print("\n=== Health Check Complete ===")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(check_services())
