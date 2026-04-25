import os
import sys
import asyncio
from playwright.async_api import async_playwright

# Mimic run.py logic
if sys.platform == 'win32' and not os.environ.get('HOME'):
    print("HOME not set. Setting to USERPROFILE...")
    os.environ['HOME'] = os.environ.get('USERPROFILE', '')
else:
    print(f"HOME matches: {os.environ.get('HOME')}")

async def main():
    print("Starting Playwright...")
    try:
        async with async_playwright() as p:
            print("Launching browser...")
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto("http://example.com")
            title = await page.title()
            print(f"Page title: {title}")
            await browser.close()
            print("Playwright check passed!")
    except Exception as e:
        print(f"Playwright check failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
