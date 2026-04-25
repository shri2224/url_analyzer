# URL Analysis Project

## System Requirements
- Python 3.8+
- Node.js & npm

## Setup

### Backend
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Frontend
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```

## Running the Project

You need to run both the backend and frontend terminals simultaneously.

### 1. Start Backend
In the `backend` directory:
```bash
python run.py
```
*The API will start at http://127.0.0.1:8000*

### 2. Start Frontend
In the `frontend` directory:
```bash
npm run dev
```
*The UI will run at http://localhost:5173*
