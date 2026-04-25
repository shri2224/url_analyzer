import asyncio
import os
import sys
from playwright.async_api import async_playwright

# Ensure HOME is set
if sys.platform == 'win32' and not os.environ.get('HOME'):
    os.environ['HOME'] = os.environ.get('USERPROFILE', '')

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Navigating to http://localhost:5173 ...")
        try:
            await page.goto("http://localhost:5173", timeout=10000)
            title = await page.title()
            print(f"Page Title: {title}")
            
            # Take screenshot
            screenshot_path = os.path.join(os.getcwd(), "frontend_verify.png")
            await page.screenshot(path=screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")
            
            if "URL Threat Analyzer" not in title and "Vite" not in title:
                print("WARNING: Title does not match expected app title.")
            else:
                print("SUCCESS: Frontend loaded successfully.")
                
        except Exception as e:
            print(f"ERROR: Failed to load frontend: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
