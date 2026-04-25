import asyncio
import base64
import re
from typing import List, Optional
from playwright.async_api import async_playwright, Page, Response
from app.models.schemas import RedirectionNode

class BrowserAgent:
    def __init__(self):
        self.nodes: List[RedirectionNode] = []

    def extract_links_regex(self, html: str) -> List[str]:
        """Extracts all hrefs from <a> tags using regex."""
        # Simple regex to find href="..."
        pattern = r'<a\s+(?:[^>]*?\s+)?href="([^"]*)"'
        return re.findall(pattern, html)

    async def trace(self, start_url: str) -> List[RedirectionNode]:
        async with async_playwright() as p:
            # Launch browser (headless=True for production)
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                ignore_https_errors=True
            )
            page = await context.new_page()

            # We will capture the chain primarily via the response of the final navigation,
            # but we can also listen to 'response' events if we need deeper debugging later.
            
            chain_nodes = []

            try:
                # Go to the page
                # Using 'domcontentloaded' is safer for sites that stream data or have long-running network requests
                try:
                    final_response = await page.goto(start_url, wait_until="domcontentloaded", timeout=45000)
                except Exception as e:
                    print(f"Navigation timeout or error for {start_url}: {e}")
                    final_response = None
                
                # Take screenshot of the final state
                screenshot_b64 = None
                try:
                    screenshot_bytes = await page.screenshot(full_page=False, timeout=5000)
                    screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")
                except Exception:
                    pass # Screenshot failure shouldn't fail the analysis
                
                if final_response:
                    # Build redirect chain by walking backwards through redirectedFrom
                    # This captures HTTP 3xx redirects handled by the browser
                    redirect_requests = []
                    current_request = final_response.request
                    
                    try:
                        while current_request.redirected_from:
                            redirect_requests.insert(0, current_request.redirected_from)
                            current_request = current_request.redirected_from
                    except Exception as e:
                        print(f"Error building redirect chain: {e}")
                    
                    # 1. Add intermediate redirects
                    for idx, req in enumerate(redirect_requests):
                        try:
                            resp = await req.response()
                            headers = await resp.all_headers() if resp else {}
                            status = resp.status if resp else 300 # Assume redirect status if missing
                        except Exception:
                            headers = {}
                            status = 0
                        
                        chain_nodes.append(RedirectionNode(
                            step=idx,
                            url=req.url,
                            status=status,
                            headers=headers,
                            screenshot=None
                        ))
                    
                    # 2. Add the final destination
                    try:
                        final_headers = await final_response.all_headers()
                        final_content = await page.content()
                        final_links = self.extract_links_regex(final_content)
                    except Exception:
                        final_headers = {}
                        final_content = ""
                        final_links = []
                    
                    chain_nodes.append(RedirectionNode(
                        step=len(chain_nodes),
                        url=final_response.url,
                        status=final_response.status,
                        headers=final_headers,
                        screenshot=screenshot_b64,
                        body_summary=final_content,
                        extracted_links=final_links
                    ))
                
                else:
                    # Timeout or navigation error, but page might have loaded content partly
                    current_url = page.url
                    try:
                        html_content = await page.content()
                        extracted_links = self.extract_links_regex(html_content)
                    except:
                        html_content = "Unable to retrieve content"
                        extracted_links = []
                    
                    chain_nodes.append(RedirectionNode(
                        step=0,
                        url=current_url if current_url != "about:blank" else start_url,
                        status=0,
                        headers={"Error": "Navigation failed or timed out"},
                        screenshot=screenshot_b64,
                        body_summary=html_content,
                        extracted_links=extracted_links
                    ))
                
                return chain_nodes

            except Exception as e:
                print(f"Critical error tracing URL: {e}")
                import traceback
                traceback.print_exc()
                # Return a distinct error node
                return [RedirectionNode(
                    step=0, 
                    url=start_url, 
                    status=599, 
                    headers={"Error-Type": "AgentCrash"}, 
                    body_summary=f"INTERNAL AGENT ERROR: {str(e)}"
                )]
            finally:
                await browser.close()
