import httpx
import asyncio

async def test_apis():
    print("Testing DomainDuck API with GET...")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://v1.api.domainduck.io/api/get/?domain=google.com&apikey=ZKLLJD5YBMJS&whois=1"
            )
            print(f"DomainDuck Status: {resp.status_code}")
            print(f"DomainDuck Response: {resp.text[:500]}")  # First 500 chars
    except Exception as e:
        print(f"DomainDuck Error: {e}")

asyncio.run(test_apis())
