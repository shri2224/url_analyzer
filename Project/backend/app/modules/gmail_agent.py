import os.path
import base64
import json
import re
from typing import List, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from datetime import datetime
import asyncio
from app.core.database import SessionLocal
from app.core import crud

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "credentials.json"
DATA_FILE = "data/email_scans.json"

class GmailAgent:
    def __init__(self):
        self.creds = None
        self.service = None
        # Ensure data directory exists (still used for credentials/token)
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)


        # Determine path to credentials (root or backend)
        if os.path.exists(CREDENTIALS_FILE):
             self.creds_path = CREDENTIALS_FILE
        elif os.path.exists(os.path.join("backend", CREDENTIALS_FILE)):
             self.creds_path = os.path.join("backend", CREDENTIALS_FILE)
        else:
             self.creds_path = CREDENTIALS_FILE # Default fallback

        # Determine path to token
        if os.path.exists(TOKEN_FILE):
             self.token_path = TOKEN_FILE
        elif os.path.exists(os.path.join("backend", TOKEN_FILE)):
             self.token_path = os.path.join("backend", TOKEN_FILE)
        else:
             self.token_path = TOKEN_FILE


    def authenticate(self, interactive=False):
        """Authenticates with Gmail API."""
        if os.path.exists(self.token_path):
            self.creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing token: {e}")
                    self.creds = None # Force re-auth
            
            if not self.creds:
                if not interactive:
                    print("Gmail authentication required. Please authenticate manually (e.g. run gmail_test.py).")
                    return False

                if not os.path.exists(self.creds_path):
                     print(f"Credentials not found at {self.creds_path}")
                     return False
                     
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.creds_path, SCOPES
                )
                # Run local server to get token
                self.creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_path, "w") as token:
                token.write(self.creds.to_json())

        try:
            self.service = build("gmail", "v1", credentials=self.creds)
            return True
        except Exception as e:
            print(f"Failed to build service: {e}")
            return False

    def get_profile_email(self):
        """Retrieves the authenticated user's email address."""
        if not self.service:
            # Try to authenticate if not already done
            if not self.authenticate():
                 return None

        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return profile.get('emailAddress')
        except Exception as e:
            print(f"Error fetching profile: {e}")
            return None

    def check_connection(self):
        """Checks if the service is active and authenticated."""
        return self.get_profile_email() is not None





    def fetch_recent_emails(self, limit=10):
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            results = self.service.users().messages().list(userId="me", maxResults=limit).execute()
            messages = results.get("messages", [])
            
            email_data = []
            for msg in messages:
                # Check DB if already scanned to avoid refetching content
                db = SessionLocal()
                try:
                    existing = crud.get_email_scan_by_id(db, msg['id'])
                except Exception:
                    existing = None
                finally:
                    db.close()

                if existing:
                    continue
                    
                full_msg = self.service.users().messages().get(userId="me", id=msg['id']).execute()
                parsed = self.parse_email(full_msg)
                if parsed:
                    email_data.append(parsed)
            
            return email_data
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []

    def parse_email(self, msg):
        try:
            payload = msg.get("payload", {})
            headers = payload.get("headers", [])
            
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(No Subject)")
            sender = next((h["value"] for h in headers if h["name"] == "From"), "(Unknown)")
            date = next((h["value"] for h in headers if h["name"] == "Date"), "")
            
            # Extract body and tracking pixels
            body_text = ""
            tracking_pixels = []
            
            if "parts" in payload:
                for part in payload["parts"]:
                    mime_type = part.get("mimeType", "")
                    data = part.get("body", {}).get("data")
                    
                    if mime_type == "text/plain" and data:
                        body_text += base64.urlsafe_b64decode(data).decode()
                    elif mime_type == "text/html" and data:
                        html = base64.urlsafe_b64decode(data).decode()
                        soup = BeautifulSoup(html, "html.parser")
                        body_text += soup.get_text() + " "
                        
                        # Extract hrefs
                        for a in soup.find_all('a', href=True):
                            body_text += f"\n{a['href']}\n"
                            
                        # Extract tracking pixels
                        for img in soup.find_all('img', src=True):
                            src = img['src']
                            width = img.get('width', '')
                            height = img.get('height', '')
                            style = img.get('style', '').lower()
                            
                            is_pixel = False
                            reasons = []
                            
                            if width == "1" or height == "1":
                                is_pixel = True
                                reasons.append(f"1x1 dimensions ({width}x{height})")
                            
                            if "display:none" in style or "visibility:hidden" in style:
                                is_pixel = True
                                reasons.append("Hidden via CSS")
                                
                            if not width and not height and "display: inline" not in style:
                                # Often trackers have no declared size
                                if "pixel" in src.lower() or "track" in src.lower() or "open" in src.lower():
                                    is_pixel = True
                                    reasons.append("Suspicious URL pattern & zero dimensions")

                            if is_pixel:
                                tracking_pixels.append({
                                    "url": src,
                                    "reasons": reasons
                                })
            else:
                 # Standard body (no parts)
                 data = payload.get("body", {}).get("data")
                 if data:
                     body_text = base64.urlsafe_b64decode(data).decode()

            # Extract Authentication-Results
            auth_results = {}
            for h in headers:
                if h["name"].lower() == "authentication-results":
                    ar_value = h["value"]
                    # Simple regex parsing for SPF, DKIM, DMARC
                    # Looking for patterns like "spf=pass", "dkim=pass", "dmarc=pass"
                    # This is a basic implementation; robust parsing might need a dedicated library
                    
                    if "spf=" in ar_value.lower():
                        match = re.search(r"spf=(\w+)", ar_value, re.IGNORECASE)
                        if match: auth_results['spf'] = match.group(1).lower()
                        
                    if "dkim=" in ar_value.lower():
                        match = re.search(r"dkim=(\w+)", ar_value, re.IGNORECASE)
                        if match: auth_results['dkim'] = match.group(1).lower()
                        
                    if "dmarc=" in ar_value.lower():
                        match = re.search(r"dmarc=(\w+)", ar_value, re.IGNORECASE)
                        if match: auth_results['dmarc'] = match.group(1).lower()
                    
                    # Store the raw header just in case
                    auth_results['raw'] = ar_value
                    break
            
            urls = self._extract_urls(body_text)
            
            return {
                "email_id": msg["id"],
                "subject": subject,
                "from": sender,
                "date": date,
                "urls": [{"url": u, "status": "pending"} for u in set(urls)], # Unique URLs
                "overall_verdict": "pending",
                "auth_results": auth_results,
                "tracking_pixels": tracking_pixels
            }
        except Exception as e:
            print(f"Error parsing email {msg.get('id')}: {e}")
            return None

    def _extract_urls(self, text):
        # Basic regex for URL extraction
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*'
        urls = re.findall(url_pattern, text)
        # Clean URLs
        clean_urls = []
        for u in urls:
             u = u.rstrip('.,)>]')
             if u.startswith('http'):
                 clean_urls.append(u)
        return clean_urls

    async def analyze_url_task(self, url, browser_agent, cti_checker, reporter):
        """Analyze a single URL with full chain trace, CTI, and AI summary."""
        print(f"Scanning URL: {url}")
        try:
            # Trace
            chain = await browser_agent.trace(url)
            
            # Check CTI
            is_malicious = False
            cti_summary = []
            
            for node in chain:
                cti = await cti_checker.check_url(node.url)
                # BUG FIX: Store CTI data back into the node so reporter can see it
                node.cti_data = cti
                
                if cti.get("verdict") == "Malicious":
                    is_malicious = True
                    cti_summary.append(f"Malware found on {node.url} (VirusTotal)")
                
                dd = cti.get("sources", {}).get("domainduck", {})
                if dd.get("age_days", 999) < 30 and dd.get("age_days") != -1:
                        cti_summary.append(f"Suspiciously young domain: {node.url} ({dd.get('age_days')} days old)")

            # Generate AI Summary using Reporter (now with CTI data in nodes)
            ai_summary = "Safe."
            try:
                detailed_report = await reporter.generate_report(chain)
                if detailed_report:
                    ai_summary = detailed_report
            except:
                pass
            
            # If CTI flagged it as malicious, PREPEND the threat info
            # so the AI report doesn't hide the real verdict
            if is_malicious:
                threat_header = "⚠️ CRITICAL THREAT DETECTED\n" + "\n".join(f"- {s}" for s in cti_summary) + "\n\n"
                ai_summary = threat_header + ai_summary
            elif chain and len(chain) > 3:
                ai_summary = f"⚠️ Suspicious: Long redirection chain ({len(chain)} hops).\n\n" + ai_summary

            status = "unsafe" if is_malicious else "safe"
            
            # Create Full Report Object
            full_report = {
                "original_url": url,
                "final_url": chain[-1].url if chain else url,
                "chain": [node.model_dump() for node in chain],
                "summary_report": ai_summary,
                "children": []
            }

            return {
                "url": url,
                "status": status,
                "explanation": ai_summary[:200] + "..." if len(ai_summary) > 200 else ai_summary,
                "full_analysis": full_report
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "url": url,
                "status": "error",
                "explanation": str(e),
                "full_analysis": None
            }

    async def scan_emails_background(self, browser_agent, cti_checker, reporter):
        """
        Background task to scan new emails.
        """
        if not self.creds:
            self.authenticate()
        
        if not self.service:
            return

        print("Fetching recent emails...")
        emails = self.fetch_recent_emails(limit=5) # Check last 5 emails
        
        # Setup DB session
        from app.core.database import SessionLocal
        from app.core import crud
        db = SessionLocal()
        
        try:
            for email_data in emails:
                email_id = email_data['email_id']
                
                # Check DB if already scanned
                existing = crud.get_email_scan_by_id(db, email_id)
                if existing:
                    continue

                print(f"Analyzing email: {email_data['subject']}")
                
                # Analyze URLs
                urls = []
                overall_verdict = "safe"
                
                for url in email_data.get('urls', []): # Changed from 'extracted_urls' to 'urls' to match parse_email output
                    # Parallel or sequential analysis
                    analysis_result = await self.analyze_url_task(url["url"], browser_agent, cti_checker, reporter) # Pass url string, not dict
                    
                    if analysis_result['status'] == 'unsafe':
                        overall_verdict = "unsafe"
                    elif analysis_result['status'] == 'error' and overall_verdict != 'unsafe':
                        overall_verdict = "error"
                        
                    urls.append(analysis_result)
                
                # Construct result
                current_account = self.get_profile_email()
                result = {
                    "email_id": email_id,
                    "subject": email_data['subject'],
                    "from": email_data['from'],
                    "date": email_data['date'],
                    "urls": urls,
                    "overall_verdict": overall_verdict,
                    "account": current_account
                }
                
                # Save to DB
                crud.create_email_scan(db, result)
                print(f"Saved scan result for {email_id}")
                
        except Exception as e:
            print(f"Error in background scan: {e}")
            import traceback
            traceback.print_exc()
        finally:
            db.close()
