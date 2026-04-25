import httpx
import base64
from typing import Dict, Any
from app.core.cti_config import VIRUSTOTAL_API_KEY, DOMAINDUCK_API_KEY
from urllib.parse import urlparse
from datetime import datetime
from dateutil import parser # Ensure python-dateutil is installed or use fallback

class CTIChecker:
    def __init__(self):
        self.vt_key = VIRUSTOTAL_API_KEY
        self.domainduck_key = DOMAINDUCK_API_KEY

    def _get_registered_domain(self, url: str) -> str:
        """Attempts to extract the registered domain from a URL."""
        try:
            parsed = urlparse(url if "://" in url else f"http://{url}")
            domain = parsed.netloc or parsed.path
            
            # Basic heuristic: strip 'www.'
            if domain.startswith("www."):
                domain = domain[4:]
            
            # Keep it simple for now (a real implementation might use tldextract)
            return domain
        except:
            return ""

    async def check_url(self, url: str) -> Dict[str, Any]:
        """
        aggregates results from available CTI sources.
        """
        results = {
            "verdict": "Clean",
            "score": 0,
            "sources": {}
        }
        
        # 1. VirusTotal
        if self.vt_key:
            vt_res = await self._check_virustotal(url)
            results["sources"]["virustotal"] = vt_res
            if vt_res.get("malicious", 0) > 0:
                results["verdict"] = "Malicious"
                results["score"] = max(results["score"], 80)

        # 2. DomainDuck (Domain Age)
        if self.domainduck_key:
            domain = self._get_registered_domain(url)
            if domain:
                dd_res = await self._check_domain_age(domain)
                results["sources"]["domainduck"] = dd_res
                # Logic: New domains might be suspicious
                if dd_res.get("age_days", 999) < 30 and dd_res.get("age_days") != -1: # Less than 30 days
                        results["score"] = max(results["score"], 50)
                        if results["verdict"] == "Clean":
                            results["verdict"] = "Suspicious"

        return results

    async def _check_virustotal(self, url: str) -> Dict[str, Any]:
        try:
            # VT requires URL to be base64 encoded
            url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"https://www.virustotal.com/api/v3/urls/{url_id}", 
                    headers={"x-apikey": self.vt_key}
                )
                
                if resp.status_code == 200:
                    data = resp.json().get("data", {}).get("attributes", {})
                    stats = data.get("last_analysis_stats", {})
                    return {
                        "malicious": stats.get("malicious", 0),
                        "stats": stats,
                        "link": f"https://www.virustotal.com/gui/url/{url_id}"
                    }
                elif resp.status_code in [401, 403]:
                    return {"error": "API Key Expired or Invalid", "error_code": 69}
                elif resp.status_code == 404:
                    return {"status": "not_found", "message": "URL not submitted to VT before"}
                else:
                    return {"error": f"VT Status {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}


    async def _check_domain_age(self, domain: str) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"https://v1.api.domainduck.io/api/get/?domain={domain}&apikey={self.domainduck_key}&whois=1",
                    timeout=10.0
                )
                
                if resp.status_code == 200:
                    data = resp.json()
                    
                    # Normalize keys
                    created_at = (data.get("CreationDate") or 
                                 data.get("creation_date") or 
                                 data.get("created_date"))
                    
                    age_days = -1
                    if created_at:
                        try:
                            # Try parsing
                            dt_created = None
                            if isinstance(created_at, list):
                                created_at = created_at[0]
                                
                            str_date = str(created_at)
                            
                            try:
                                dt_created = parser.parse(str_date)
                            except:
                                # Fallback manual parsing if needed, but parser is robust
                                pass
                                
                            if dt_created:
                                # Make timezone aware if not
                                if dt_created.tzinfo is None:
                                   dt_created = dt_created.replace(tzinfo=datetime.now().astimezone().tzinfo)
                                
                                now = datetime.now(dt_created.tzinfo)
                                age_days = (now - dt_created).days
                        except Exception as e:
                            print(f"Date parsing error for {domain}: {e}")
                            
                    registrar = (data.get("Registrar") or 
                                data.get("registrar") or
                                data.get("RegistrarName"))
                    
                    return {
                        "creation_date": str(created_at) if created_at else None,
                        "age_days": age_days,
                        "registrar": registrar,
                        "domain": domain
                    }
                elif resp.status_code in [401, 403]:
                    return {"error": "API Key Expired or Invalid", "error_code": 69}
                return {"status": f"DomainDuck Code {resp.status_code}", "error": resp.text}
        except Exception as e:
            return {"error": str(e)}
