import asyncio
import os
import sys
# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.modules.reporter import Reporter
from app.models.schemas import RedirectionNode

async def test_report_generation():
    print("Initializing Reporter...", flush=True)
    reporter = Reporter()
    
    # 1. Create a mock RedirectionNode with Malicious CTI data
    mock_node_malicious = RedirectionNode(
        step=0,
        url="http://malicious-test.com",
        status=200,
        headers={},
        cti_data={
            "verdict": "Malicious",
            "score": 80,
            "sources": {
                "virustotal": {
                    "malicious": 5,
                    "stats": {"malicious": 5, "suspicious": 0, "harmless": 85},
                    "link": "https://www.virustotal.com/gui/url/test-malicious"
                }
            }
        }
    )

    # 2. Create a mock RedirectionNode with Clean CTI data
    mock_node_clean = RedirectionNode(
        step=0,
        url="http://clean-test.com",
        status=200,
        headers={},
        cti_data={
            "verdict": "Clean",
            "score": 0,
            "sources": {
                "virustotal": {
                    "malicious": 0,
                    "stats": {"malicious": 0, "suspicious": 0, "harmless": 90},
                    "link": "https://www.virustotal.com/gui/url/test-clean"
                }
            }
        }
    )

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_report_output.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        print("\n--- Testing Malicious Report ---", flush=True)
        report_mal = await reporter.generate_report([mock_node_malicious])
        print(report_mal, flush=True)
        f.write("--- MALICIOUS REPORT ---\n")
        f.write(report_mal + "\n\n")

        print("\n--- Testing Clean Report ---", flush=True)
        report_clean = await reporter.generate_report([mock_node_clean])
        print(report_clean, flush=True)
        f.write("--- CLEAN REPORT ---\n")
        f.write(report_clean + "\n")
    
    print(f"Reports written to {output_path}")

if __name__ == "__main__":
    asyncio.run(test_report_generation())
