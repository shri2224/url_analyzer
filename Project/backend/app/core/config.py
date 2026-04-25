import os
from dotenv import load_dotenv

# Load .env FIRST so all os.getenv() calls pick up .env values
load_dotenv()

# CTI API Keys
VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")  # Never hardcode API keys as defaults
ISMALICIOUS_API_KEY = os.getenv("ISMALICIOUS_API_KEY", "YOUR_ISMALICIOUS_KEY_HERE")
MISP_URL = os.getenv("MISP_URL", "https://misppriv.circl.lu") # Example/Placeholder
MISP_KEY = os.getenv("MISP_KEY", "YOUR_MISP_KEY_HERE")

# Ollama / AI Configuration
# If using a cloud provider for Ollama/Llama, specify the URL and Key here
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434") 
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "YOUR_OPTIONAL_KEY_HERE") 
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:120b") 
