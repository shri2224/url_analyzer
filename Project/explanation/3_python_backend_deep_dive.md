# Python Backend Deep Dive

## 1. Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routes.py      # The API Endpoints
│   ├── core/
│   │   ├── database.py    # Database connection logic
│   │   └── crud.py        # Create, Read, Update, Delete functions
│   ├── models/
│   │   ├── models.py      # SQLAlchemy Database Models
│   │   └── schemas.py     # Pydantic Data Models (Input/Output validation)
│   └── modules/
│       ├── browser_agent.py # Headless browser logic
│       ├── gmail_agent.py   # Email fetching logic
│       ├── cti_checker.py   # VirusTotal / Intel logic
│       └── reporter.py      # AI Summary logic
├── main.py                # Entry point (FastAPI app)
└── run.py                 # Startup script
```

## 2. Core Modules in Detail

### A. The Browser Agent (`browser_agent.py`)
This is the "eyes" of the system.
- **Key Function**: `trace(url: str)`
- **How it works**:
  1. Launches a Playwright browser context.
  2. Sets User-Agent to mimic a real desktop browser.
  3. Navigates to the URL.
  4. While navigating, it listens to the `response` event to capture redirection hops (301, 302, meta-refresh).
  5. Waits for the page to load (`domcontentloaded`).
  6. Takes a screenshot (`page.screenshot()`).
  7. Extracts the page text (`document.body.innerText`) for analysis.
  8. Returns a list of `RedirectionNode` objects (each representing one step).

### B. The Gmail Agent (`gmail_agent.py`)
This is the "watcher".
- **Authentication**: Uses `google_auth_oauthlib` to get a token via OAuth flow. Stores token in `token.json`.
- **Fetching**: `fetch_recent_emails()` calls the Gmail API (`users.messages.list`).
- **Parsing**: `parse_email()` decodes the raw email body (Base64) into plain text/HTML and extracts URLs using regex.
- **Background Task**: `scan_emails_background()` runs periodically or manually. It loops through emails, checks DB if already scanned, analyzes URLs via `browser_agent`, and saves results.

### C. The Reporter (`reporter.py`)
This is the "brain".
- **Key Function**: `generate_report(chain)`
- **How it works**:
  1. Takes the redirection chain and technical data.
  2. Constructs a prompt for Ollama: "You are a cyber security analyst. Analyze this...".
  3. Sends the prompt to `http://localhost:11434/api/generate`.
  4. Returns the AI's response text.
- **Threat Scan**: Also performs regex checks for known malicious patterns (e.g., "login", "update payment", "verify account") in the page text.

### D. The CTI Checker (`cti_checker.py`)
This is the "intel".
- **Key Function**: `check_url(url)`
- **How it works**:
  1. Queries VirusTotal API with the URL.
  2. If flagged by >2 vendors, marks as Malicious.
  3. Queries DomainDuck (or WhoIs) for domain age. Newly registered domains (<30 days) are flagged as suspicious.

## 3. The API Layer (`routes.py`)

This file ties everything together.
- Defines standard REST endpoints: `GET`, `POST`, `DELETE`.
- **Dependency Injection**: Uses `Depends(get_db)` to give each request a fresh database session.
- **Background Tasks**: Handled via `FastAPI.BackgroundTasks` so the user gets an immediate response ("Scan started") while the heavy analysis runs in the background.

## 4. The Data Layer (`database.py`, `models.py`, `crud.py`)

We use **SQLAlchemy ORM**.
- **`database.py`**: Creates the engine (`create_engine`) and session factory.
- **`models.py`**: Defines Python classes that map to SQL tables.
  ```python
  class UrlScan(Base):
      __tablename__ = "url_scans"
      id = Column(Integer, primary_key=True)
      url = Column(String)
      full_report_json = Column(JSON) # JSON support in SQLite!
  ```
- **`crud.py`**: Functions to interact with the DB. E.g., `create_url_scan()` adds a row, `get_url_scans()` queries rows with pagination.
