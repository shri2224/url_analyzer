import httpx
import asyncio

async def test():
    client = httpx.AsyncClient()
    resp = await client.get('https://v1.api.domainduck.io/api/get/?domain=iopex.com&apikey=ZKLLJD5YBMJS&whois=1')
    print(f'Status: {resp.status_code}')
    data = resp.json()
    print(f'CreationDate: {data.get("CreationDate")}')
    print(f'Registrar: {data.get("Registrar")}')
    await client.aclose()

asyncio.run(test())
