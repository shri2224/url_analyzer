from app.modules.gmail_agent import GmailAgent
import time

# Shared Singleton
gmail_agent = GmailAgent()

# Extension Heartbeat State
# Timestamp of last received heartbeat (Unix epoch)
last_extension_heartbeat = 0
