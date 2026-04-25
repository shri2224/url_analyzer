import ollama
from typing import List
from app.models.schemas import RedirectionNode
from app.core.config import OLLAMA_API_URL, OLLAMA_API_KEY, OLLAMA_MODEL

class Reporter:
    def __init__(self, model_name: str = OLLAMA_MODEL):
        self.model_name = model_name
        # If using a cloud provider that matches Ollama API or a remote Ollama instance
        self.client = ollama.AsyncClient(host=OLLAMA_API_URL) 
        # Note: If the cloud provider uses OpenAI compatible API, we might need a different client (e.g. OpenAI SDK)
        # But 'ollama' library allows setting 'host'. 
        
    async def generate_report(self, chain: List[RedirectionNode]) -> str:
        """
        Generates a summary report using Ollama based on the redirection chain.
        """
        chain_desc = "\n".join([
            f"Step {node.step}: {node.url} (Status: {node.status})\n"
            f"  - CTI Data: {node.cti_data}\n"
            f"  - Extracted Links Count: {len(node.extracted_links) if node.extracted_links else 0}"
            for node in chain
        ])
        
        prompt = f"""
        Analyze the following URL redirection chain and CTI data.
        
        Data:
        {chain_desc}
        
        Please provide a report in the following STRICT format:
        
        ## VirusTotal Result
        (Summarize VirusTotal stats from the data if available. If clean, say Clean.)
        
        ## Domain Intelligence
        (Summarize Domain Age and Registrar info. Highlight if the domain is suspiciously new (< 30 days).)
        
        ## Malicious Code Explanation
        (If any malicious indicators were found, explain them here. Otherwise, state 'No malicious code found'.)
        """
        
        try:
            response = await self.client.chat(model=self.model_name, messages=[
                {'role': 'user', 'content': prompt},
            ])
            return response['message']['content']
        except Exception as e:
            return f"Error generating AI report: {str(e)}. Check URL: {OLLAMA_API_URL}"

    async def analyze_code(self, html_content: str, headers: dict) -> str:
        """
        Performs a code-level security analysis using Ollama.
        """
        prompt = f"""
        Perform a code-level security analysis on the following HTML content and Headers.
        
        Headers:
        {headers}
        
        HTML Content (Truncated):
        {html_content[:4000]}
        
        Output format:
        1. Short Summary of the page content.
        2. Malicious Code Snippets (if any found, paste them here).
        3. Explanation of why it is malicious.
        """
        try:
            response = await self.client.chat(model=self.model_name, messages=[
                {'role': 'user', 'content': prompt},
            ])
            return response['message']['content']
        except Exception as e:
            return f"Error analyzing code: {str(e)}"
