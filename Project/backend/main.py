from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.routes import router
from app.api.health import health_router

from app.api.routes import browser_agent, cti_checker, reporter
import app.state as state
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background polling loop
    task = asyncio.create_task(background_polling())
    yield
    # Cleanup task on shutdown if needed
    task.cancel()

app = FastAPI(title="Redirection Detector API", lifespan=lifespan)

async def background_polling():
    # Defer first run so startup_event can complete without blocking
    await asyncio.sleep(10)
    while True:
        try:
            print("Running scheduled Gmail scan...")
            # Run blocking authenticate() in a thread so we don't freeze the event loop
            await asyncio.to_thread(state.gmail_agent.authenticate)
            await state.gmail_agent.scan_emails_background(browser_agent, cti_checker, reporter)
        except Exception as e:
            print(f"Background scan error: {e}")
        await asyncio.sleep(300)  # 5 minutes

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production: replace with specific frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
app.include_router(health_router, prefix="/api")

@app.get("/api/ping")
def ping():
    return {"status": "ok"}

@app.get("/")
def read_root():
    return {"message": "Redirection Detector API is running"}
