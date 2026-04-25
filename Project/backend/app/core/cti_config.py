import os
from dotenv import load_dotenv

load_dotenv()

VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")
DOMAINDUCK_API_KEY = os.getenv("DOMAINDUCK_API_KEY")
