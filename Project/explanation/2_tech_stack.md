# Tech Stack & Rationale

## 1. Frontend: React + Vite + TailwindCSS
- **React**: Component-based UI library allows us to build reusable widgets like the `RedirectionChain` visualizer.
- **Vite**: Provides instant server start and hot module replacement (HMR), making development extremely fast.
- **TailwindCSS**: Enabling rapid styling without leaving the component file. We use it for the "dark mode" cyber-security aesthetic (slate grays, emerald greens for safe, red for malicious).

## 2. Backend: Python + FastAPI
- **Python**: The language of choice for security tools and AI.
  - Excellent libraries for browser automation (`playwright`), data handling (`pydantic`), and AI integration (`ollama`).
- **FastAPI**: A modern, high-performance web framework for building APIs with Python 3.10+ based on standard Python type hints.
  - **Why FastAPI?** It automatically generates interactive API docs (`/docs`), validates data using Pydantic models (crucial for security inputs), and supports asynchronous programming (`async/await`) needed for handling multiple browser tabs concurrently.

## 3. Browser Automation: Playwright
- **Playwright**: A powerful library to control headless browsers (Chromium, Firefox, WebKit).
- **Why not Selenium?** Playwright is faster, more reliable, and handles modern web features (shadow DOM, network interception) much better. It allows us to:
  - Capture full-page screenshots.
  - Intercept network requests to analyze headers and redirection chains.
  - Block distinct resource types (e.g., images/fonts) to speed up scans.

## 4. AI & Intelligence: Ollama + VirusTotal
- **Ollama**: Represents a local Large Language Model (LLM) running on your machine.
  - **Role**: Takes raw technical data (HTML, headers, redirection hops) and turns it into a human-readable summary. "This page mimics a bank login."
- **VirusTotal API**: The industry standard for checking if a URL or file hash is malicious. Provides "reputation" scores from 70+ security vendors.

## 5. Database: SQLite + SQLAlchemy
- **SQLite**: A self-contained, serverless, zero-configuration, transactional SQL database engine.
  - **Why?** Perfect for a local security tool. No need to install a separate database server.
- **SQLAlchemy**: The Python SQL toolkit and Object Relational Mapper (ORM).
  - **Role**: Allows us to interact with the database using Python classes (`UrlScan`, `EmailScan`) instead of writing raw SQL queries.
