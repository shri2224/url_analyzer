import json
import sys

try:
    with open("full_response.json", "r", encoding="utf-16") as f: # PowerShell Out-File defaults to UTF-16
        data = json.load(f)
except Exception:
    try:
         with open("full_response.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        sys.exit(1)

print("Analyzing JSON structure...")
if "chain" in data:
    for i, node in enumerate(data["chain"]):
        print(f"\n--- Node {i} ---")
        cti = node.get("cti_data", {})
        if cti:
            print("CTI Data Keys:", list(cti.keys()))
            if "sources" in cti:
                print("Sources Keys:", list(cti["sources"].keys()))
                if "domainduck" in cti["sources"]:
                    print("DomainDuck Data:", cti["sources"]["domainduck"])
                else:
                    print("MISSING 'domainduck' in sources")
            else:
                print("MISSING 'sources' in cti_data")
        else:
            print("NO CTI DATA")
else:
    print("NO CHAIN FOUND")
