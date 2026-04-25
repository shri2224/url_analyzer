import sys
import os
import asyncio
import json

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.modules.reporter import Reporter
except ImportError as e:
    print(f"ImportError: {e}", flush=True)
    sys.exit(1)

async def main():
    print("Initializing Reporter...", flush=True)
    # Mock OLLAMA_API_URL if needed, but Reporter grabs it from config. 
    # Provided config.py exists and has defaults, it should work.
    try:
        reporter = Reporter()
    except Exception as e:
        print(f"Failed to initialize Reporter: {e}", flush=True)
        return

    patterns = reporter.mal_patterns
    print(f"Loaded {len(patterns)} patterns.", flush=True)
    
    if not patterns:
        print("ERROR: No patterns loaded! Check dataset.json path.", flush=True)
        # Debug: print where it looked
        print(f"Expected path: {os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'dataset.json'))}", flush=True)
        return

    # Test scanning logic
    # Pattern ID 1 is "eval(atob("
    test_html_dropper = "<html><body><script>eval(atob('dGVzdA=='));</script></body></html>"
    print(f"\nTesting scan with malicious HTML (Dropper): {test_html_dropper}", flush=True)
    matches = reporter._scan_patterns(test_html_dropper)
    print(f"Found {len(matches)} matches.", flush=True)
    
    found_dropper = False
    for m in matches:
        print(f" - Match: ID:{m['id']} Type:{m['type']} Category:{m['category']}", flush=True)
        if m['type'] == 'js_obfuscation' and 'eval(' in m['matched_patterns']:
            found_dropper = True

    if found_dropper:
        print("SUCCESS: Dropper pattern detected.", flush=True)
    else:
        print("FAILURE: Dropper pattern NOT detected.", flush=True)

    # Test clean HTML
    test_html_clean = "<html><body><h1>Hello World</h1></body></html>"
    print(f"\nTesting scan with clean HTML: {test_html_clean}", flush=True)
    matches_clean = reporter._scan_patterns(test_html_clean)
    print(f"Found {len(matches_clean)} matches.", flush=True)
    
    if len(matches_clean) == 0:
        print("SUCCESS: Clean HTML has no matches.", flush=True)
    else:
        print("FAILURE: Clean HTML triggered false positives.", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
