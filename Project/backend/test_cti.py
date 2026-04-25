import sys
sys.path.insert(0, 'D:/Url/Project/backend')

from app.modules.cti_checker import CTIChecker
import asyncio

async def test():
    checker = CTIChecker()
    result = await checker._check_domain_age('iopex.com')
    print("Domain Age Result:")
    print(result)

asyncio.run(test())
