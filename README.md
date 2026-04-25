# URL Threat Analyzer ("Redirection Detective")

URL Threat Analyzer is a cybersecurity tool that helps users detect malicious, phishing, or suspicious URLs — including those found in emails. When you paste a URL into the tool, it opens the URL in a headless browser, follows every redirect hop-by-hop, checks each URL against threat intelligence databases, scans the final HTML for malicious patterns, and runs a local AI model to generate a detailed security analysis report.

It also integrates with Gmail to automatically scan emails for dangerous links, and includes a Chrome Extension for quick scanning while browsing.

## 🌟 Features

- **Deep Browser Tracing:** Uses Playwright to follow HTTP and JavaScript-driven redirects.
- **Threat Intelligence (CTI):** Integrates with VirusTotal API, DomainDuck API, and a local signature dataset (101 malicious code patterns).
- **Local AI Analysis:** Uses Ollama running locally to generate human-readable security reports without sending data to the cloud.
- **Gmail Integration:** Automatically scans incoming emails for malicious links, tracking pixels, and validates SPF/DKIM/DMARC headers.
- **Chrome Extension:** Right-click any link to analyze it instantly.
- **Dashboard:** React-based dashboard to view the redirection chain, AI analysis, email scan results, and system health.

## 🛠️ Tech Stack

- **Backend:** Python 3.13, FastAPI, Uvicorn, SQLAlchemy (SQLite), Playwright
- **Frontend:** React 18, Vite, Custom CSS
- **AI/LLM:** Ollama (Local)
- **APIs:** VirusTotal, DomainDuck, Google OAuth 2.0 (Gmail API)

---

## 🔍 How It Works (The Analysis Pipeline)

When a URL is submitted for analysis, the system performs the following step-by-step pipeline:

1. **Browser Trace:** A headless Chromium browser (via Playwright) navigates to the URL. It silently follows every single redirect (both HTTP `3xx` codes and JavaScript-driven redirects), recording each hop along the way.
2. **Data Extraction:** At the final destination, the headless browser takes a full screenshot of the page and extracts all links and HTML content from the fully rendered page.
3. **Threat Enrichment (CTI):** Every URL in the redirect chain is queried against VirusTotal (for antivirus engine flags) and DomainDuck (to flag newly registered, suspicious domains).
4. **Dataset Scan:** The final HTML is scanned against a local dataset of known malicious code patterns (e.g., credential harvesters, crypto stealers, droppers).
5. **AI Code Analysis:** The extracted HTML, headers, and dataset matches are sent to a local LLM via Ollama. The AI analyzes the code structure and generates a detailed, human-readable security report explaining the threat verdict.

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed and set up:

1. **Python 3.13+**
2. **Node.js** (v18+ recommended)
3. **Ollama:** Download from [ollama.com](https://ollama.com/) and run it locally.
   - Pull a model (e.g., `llama3:8b`):
     ```bash
     ollama pull llama3:8b
     ```
4. **API Keys:**
   - **VirusTotal API Key:** Get a free key at [virustotal.com](https://www.virustotal.com/)
   - **DomainDuck API Key:** Get a key from [domainduck.io](https://domainduck.io)
   - **Google Cloud Console:** Create an OAuth 2.0 Client ID (Desktop App) for Gmail integration and download `credentials.json`.

---

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-github-repo-url>
cd Project
```

### 2. Backend Setup

Open a terminal and navigate to the `backend` directory:

```bash
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browser binaries
playwright install chromium
```

#### Configuration (.env)
Create a `.env` file in the `backend` directory with the following variables:

```env
VIRUSTOTAL_API_KEY=your_virustotal_api_key
OLLAMA_API_URL=http://localhost:11434
OLLAMA_API_KEY=
OLLAMA_MODEL=llama3:8b
DOMAINDUCK_API_KEY=your_domainduck_api_key
```

Place your downloaded `credentials.json` (for Gmail OAuth) in the `backend` directory.

### 3. Frontend Setup

Open a new terminal and navigate to the `frontend` directory:

```bash
cd frontend

# Install Node.js dependencies
npm install
```

---

## 💻 Running the Application

### Start the Backend Server

In your backend terminal (with the virtual environment activated):

```bash
cd backend
python run.py
```
> The API will be available at `http://127.0.0.1:8000`
> API Documentation (Swagger): `http://127.0.0.1:8000/docs`

### Start the Frontend Server

In your frontend terminal:

```bash
cd frontend
npm run dev
```
> The dashboard will be available at `http://localhost:5173`

---

## 🧩 Chrome Extension Setup

1. Open Google Chrome and go to `chrome://extensions/`
2. Enable **Developer mode** (toggle in the top right corner).
3. Click **Load unpacked** and select the `extension` folder in this project directory.
4. The extension will now be available in your browser to scan links.

---

## 🛡️ Security & Privacy

- **Local Execution:** All AI analysis runs locally via Ollama. No page content is sent to third-party AI clouds.
- **Isolation:** Headless Chromium isolates potentially malicious pages from your actual browser.
- **Read-Only Email Access:** Gmail integration uses read-only scopes. It cannot send or delete emails.

