import urllib.request
import json
import time

print("Waiting for backend...")
time.sleep(5)

url = "http://127.0.0.1:8000/api/health/full"
try:
    print(f"Requesting {url}...")
    with urllib.request.urlopen(url) as response:
        if response.status == 200:
            data = json.loads(response.read().decode())
            print("\n✅ API Health Check PASSED")
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ Failed with {response.status}")
except Exception as e:
    print(f"❌ Error: {e}")
