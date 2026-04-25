# System Design: Redirection Detective

## 1. Overview
Redirection Detective is a security analysis tool designed to inspect suspicious URLs and email links. It "detonates" (visits) URLs in a sandboxed headless browser to trace redirection chains, capturing technical details at every hop, and using AI to generate human-readable threat reports.

## 2. High-Level Architecture

The system follows a classic **client-server architecture**:

```mermaid
graph TD
    User[User (Browser)] -->|HTTP/React| Frontend[Frontend (Vite + React)]
    Frontend -->|REST API| Backend[Backend (FastAPI)]
    
    subgraph "Backend Services"
        Backend -->|Control| Browser[Headless Browser (Playwright)]
        Backend -->|Query| CTI[CTI Services (VirusTotal, DomainDuck)]
        Backend -->|Prompt| AI[Local LLM (Ollama)]
        Backend -->|Read/Write| DB[(SQLite Database)]
        Backend -->|Poll| Gmail[Gmail API]
    end
    
    Browser -->|Visit| Internet[Suspicious Sites]
```

## 3. Core Components

### A. Frontend (The Dashboard)
- **Role**: User Interface for submitting URLs and viewing reports.
- **Tech**: React, Vite, TailwindCSS.
- **Key Features**:
  - Real-time redirection chain visualization (hops, status codes).
  - "Inbox Scan" view to see threats in recent emails.
  - Interactive history and system health monitoring.

### B. Backend (The Engine)
- **Role**: Orchestrates analysis, manages data, and talks to external services.
- **Tech**: Python 3.10+, FastAPI.
- **Key Modules**:
  1.  **Browser Agent**: Controls a headless Chromium browser to safely visit URLs. It captures extensive data: HTTP headers, IP addresses, screenshots, and page text.
  2.  **CTI Checker**: Queries Cyber Threat Intelligence sources (VirusTotal) to check if a domain is known to be malicious.
  3.  **Reporter (AI)**: Sends collected data to a local LLM (Ollama) to generate a summary explaining *why* a URL is dangerous (e.g., "This is a phishing site mimicking Microsoft Login").
  4.  **Gmail Agent**: Background service that periodically checks the user's Gmail inbox for new emails, extracts links, and automatically scans them.
  5.  **Database**: SQLite database (`sql_app.db`) stores analysis history permanently.

## 4. Data Flow

### Scenario 1: Manual URL Analysis
1.  User enters `http://bit.ly/sus` in Frontend.
2.  Frontend sends `POST /api/analyze` to Backend.
3.  Backend spawns a **Browser Agent** task.
4.  Browser follows redirects: `bit.ly` -> `malicious.com`.
5.  For each hop, Backend:
    - Captures screenshot & headers.
    - Checks VirusTotal (is `malicious.com` flagged?).
    - Extracts page text.
6.  Backend compiles all data into a `chain`.
7.  Backend sends the chain to **Ollama (AI)** for a summary.
8.  Backend saves the full report to **SQLite**.
9.  Backend returns the report to Frontend for display.

### Scenario 2: Background Email Scan
1.  **Gmail Agent** wakes up every 5 minutes.
2.  Fetches the last 5 emails via Google API.
3.  Extracts all links (e.g., `http://login-update.com`).
4.  Checks **Database**: "Have we scanned this URL before?"
    - *Yes*: Skip.
    - *No*: Run analysis (same steps as Manual Analysis).
5.  Saves the result to the database with the verdict (Safe/Malicious).
6.  Frontend "Inbox" tab polls the API to show new results.
