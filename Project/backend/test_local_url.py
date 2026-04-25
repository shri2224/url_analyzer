import subprocess
import time
import requests
import sys
import os

# Configuration
TEST_DIR = r"d:\Url\version2\Urltester"
PORT = 8081
URL_TO_TEST = f"http://localhost:{PORT}/test_page_3.html"
BACKEND_API = "http://127.0.0.1:8000/api/analyze"

def main():
    # 1. Start HTTP Server
    print(f"Starting server in {TEST_DIR} on port {PORT}...")
    server_process = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(PORT)],
        cwd=TEST_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    try:
        time.sleep(2) # Wait for server to start
        
        # 2. Trigger Analysis
        print(f"Analyzing {URL_TO_TEST} via {BACKEND_API}...")
        response = requests.post(BACKEND_API, json={"url": URL_TO_TEST})
        
        if response.status_code == 200:
            result = response.json()
            # Debug: Print raw result to understand structure
            import json
            print(json.dumps(result, indent=2))
            
            print("\n--- ANALYSIS REPORT ---")
            print(f"Final URL: {result.get('final_url')}")
            
            summary = result.get('summary_report', {})
            # Handle if summary is None or string
            if isinstance(summary, str):
                print(f"Summary (raw): {summary}")
                summary = {}
            elif summary is None:
                summary = {}

            print(f"Verdict: {summary.get('verdict')}")
            print(f"Risk Score: {summary.get('risk_score')}")
            
            print("\nRedirect Chain:")
            for node in result.get('chain', []):
                # Debug check
                if isinstance(node, str):
                    print(f" -> {node} (String Node?)")
                    continue
                    
                print(f" -> {node.get('url')} ({node.get('status_code')})")
                cti = node.get('cti_data', {})
                if cti and cti.get('verdict') != 'Clean':
                     print(f"    [!] Threat detected: {cti.get('verdict')} ({cti.get('score')})")

            
            if summary.get('verdict') == "Malicious":
                print("\n[!] MALICIOUS CONTENT DETECTED [!]")
            else:
                print("\n[+] URL appears safe.")
                
        else:
            print(f"Error: Backend returned {response.status_code}")
            print(response.text)
            
    finally:
        # 3. Cleanup
        print("\nStopping test server...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    main()
