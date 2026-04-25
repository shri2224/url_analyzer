import sys
import asyncio
import uvicorn

if __name__ == "__main__":
    if sys.platform == 'win32':
        # Enforce ProactorEventLoopPolicy for Playwright on Windows
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Run Uvicorn
    # reload=False is required on Windows to ensure the ProactorEventLoopPolicy is correctly inherited/maintained.
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
