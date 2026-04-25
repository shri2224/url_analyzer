import os

# CTI API Keys
VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY", "7da00bf716a172be03454ebe1013e2edabecd1b0fa4f42162989ea4d38c2fff0")
ISMALICIOUS_API_KEY = os.getenv("ISMALICIOUS_API_KEY", "YOUR_ISMALICIOUS_KEY_HERE")
MISP_URL = os.getenv("MISP_URL", "https://misppriv.circl.lu") # Example/Placeholder
MISP_KEY = os.getenv("MISP_KEY", "YOUR_MISP_KEY_HERE")

from dotenv import load_dotenv
load_dotenv()

# Ollama / AI Configuration
# If using a cloud provider for Ollama/Llama, specify the URL and Key here
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434") 
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "YOUR_OPTIONAL_KEY_HERE") 
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:120b") 
