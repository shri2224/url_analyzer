import httpx
import asyncio

async def test():
    api_key = "ZKLLJD5YBMJS"
    
    domains = ["iopex.com", "www.iopex.com"]
    
    async with httpx.AsyncClient() as client:
        for d in domains:
            print(f"\nTesting: {d}")
            try:
                resp = await client.get(
                    f"https://v1.api.domainduck.io/api/get/?domain={d}&apikey={api_key}&whois=1",
                    timeout=10.0
                )
                print(f"Status: {resp.status_code}")
                # Print first 200 chars or error message
                print(f"Response: {resp.text[:200]}")
            except Exception as e:
                print(f"Error: {e}")

asyncio.run(test())
