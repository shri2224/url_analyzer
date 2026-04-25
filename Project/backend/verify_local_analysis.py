import asyncio
import httpx
import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.modules.reporter import Reporter

async def test_local_page_analysis():
    url = "http://localhost:8081/test_page_1.html"
    print(f"Fetching {url}...", flush=True)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            if response.status_code != 200:
                print(f"Failed to fetch page. Status: {response.status_code}", flush=True)
                return
            html = response.text
            headers = dict(response.headers)
        except Exception as e:
            print(f"Error fetching page: {e}", flush=True)
            return

    print("Page fetched. Analyzing...", flush=True)
    
    reporter = Reporter()
    
    # 1. Check dataset pattern matches
    matches = reporter._scan_patterns(html)
    print(f"\nDataset Pattern Matches: {len(matches)}", flush=True)
    for m in matches:
        print(f"  - [ID:{m['id']}] {m['type']} / {m['category']}: {m['description']}", flush=True)
        print(f"    Matched: {', '.join(m['matched_patterns'])}", flush=True)

    # 2. Run full AI analysis
    print("\nRunning AI Code Analysis...", flush=True)
    report = await reporter.analyze_code(html, headers)

    # Write to file for reliable reading
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_local_output.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"=== DATASET MATCHES ({len(matches)}) ===\n")
        for m in matches:
            f.write(f"  [ID:{m['id']}] {m['type']} / {m['category']}: {m['description']}\n")
            f.write(f"    Matched: {', '.join(m['matched_patterns'])}\n")
        f.write(f"\n=== AI ANALYSIS ===\n")
        f.write(report)
    
    print(f"\nFull results written to: {output_path}", flush=True)
    print("\n--- AI Analysis Result ---", flush=True)
    print(report, flush=True)

if __name__ == "__main__":
    asyncio.run(test_local_page_analysis())
