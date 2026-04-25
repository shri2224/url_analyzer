import ollama
import json
import os
import re
from typing import List, Dict, Any
from app.models.schemas import RedirectionNode
from app.core.config import OLLAMA_API_URL, OLLAMA_API_KEY, OLLAMA_MODEL

# Path to the malicious code pattern dataset
DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "dataset.json")

class Reporter:
    def __init__(self, model_name: str = OLLAMA_MODEL):
        self.model_name = model_name
        self.client = ollama.AsyncClient(host=OLLAMA_API_URL)
        self.mal_patterns = self._load_dataset()
        print(f"[Reporter] Loaded {len(self.mal_patterns)} malicious code patterns from dataset")

    def _load_dataset(self) -> List[Dict[str, Any]]:
        """Load the malicious code pattern dataset (standard JSON array)."""
        try:
            # Try multiple paths
            paths_to_try = [
                DATASET_PATH,
                os.path.join("dataset.json"),
                os.path.join("backend", "dataset.json"),
                os.path.join(os.path.dirname(__file__), "..", "..", "dataset.json"),
            ]
            
            dataset_path = None
            for p in paths_to_try:
                resolved = os.path.abspath(p)
                if os.path.exists(resolved):
                    dataset_path = resolved
                    break
            
            if not dataset_path:
                print(f"[Reporter] WARNING: dataset.json not found in any expected location")
                return []
            
            with open(dataset_path, "r", encoding="utf-8-sig") as f:
                content = f.read().strip()
            
            if not content:
                return []

            # Try parsing as a standard JSON array first (new format)
            try:
                data = json.loads(content)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return [data]
            except json.JSONDecodeError:
                pass

            # Fallback for successive JSON objects (old format)
            patterns = []
            decoder = json.JSONDecoder()
            pos = 0
            while pos < len(content):
                stripped = content[pos:].lstrip()
                if not stripped:
                    break
                pos = len(content) - len(stripped)
                try:
                    obj, end = decoder.raw_decode(content, pos)
                    patterns.append(obj)
                    pos += end
                except json.JSONDecodeError:
                    next_newline = content.find('\n', pos)
                    if next_newline == -1:
                        break
                    pos = next_newline + 1
            return patterns
                    
        except Exception as e:
            print(f"[Reporter] Error loading dataset: {e}")
            return []

    def _scan_patterns(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Pre-scan HTML content against the malicious pattern dataset.
        Returns a list of matched pattern entries with match details.
        """
        matches = []
        content_lower = html_content.lower()
        
        for entry in self.mal_patterns:
            matched_patterns = []
            for pattern in entry.get("patterns", []):
                # Case-insensitive search for each pattern string
                if pattern.lower() in content_lower:
                    matched_patterns.append(pattern)
            
            if matched_patterns:
                matches.append({
                    "id": entry.get("id"),
                    "type": entry.get("type"),
                    "category": entry.get("category"),
                    "description": entry.get("description"),
                    "matched_patterns": matched_patterns,
                    "example": entry.get("example", ""),
                })
        
        return matches

    def _build_dataset_reference(self) -> str:
        """Build a condensed reference of ALL dataset categories for the AI prompt."""
        categories = {}
        for entry in self.mal_patterns:
            cat = entry.get("category", "unknown")
            if cat not in categories:
                categories[cat] = {
                    "types": set(),
                    "patterns": [],
                    "description": entry.get("description", "")
                }
            categories[cat]["types"].add(entry.get("type", ""))
            categories[cat]["patterns"].extend(entry.get("patterns", []))
        
        lines = []
        for cat, info in categories.items():
            unique_patterns = list(set(info["patterns"]))[:8]  # Cap for prompt size
            lines.append(f"- **{cat}** ({', '.join(info['types'])}): Look for: {', '.join(unique_patterns)}")
        
        return "\n".join(lines)

    def reload_dataset(self) -> int:
        """Reloads the dataset from disk. Returns count of loaded patterns."""
        self.mal_patterns = self._load_dataset()
        print(f"[Reporter] Reloaded dataset. Count: {len(self.mal_patterns)}")
        return len(self.mal_patterns)

    def scan_threats(self, html_content: str) -> Dict[str, Any]:
        """
        Public method to scan HTML against the dataset.
        Returns a structured result with matches and a verdict.
        """
        matches = self._scan_patterns(html_content)
        
        # Determine severity based on matches
        high_severity_categories = {"dropper", "credential_harvest", "inline_malware", "redirect_chain", "c2_beacon", "crypto_stealer"}
        has_high_severity = any(m["category"] in high_severity_categories for m in matches)
        
        if has_high_severity or len(matches) >= 3:
            verdict = "Malicious"
        elif len(matches) >= 1:
            verdict = "Suspicious"
        else:
            verdict = "Clean"
        
        return {
            "verdict": verdict,
            "match_count": len(matches),
            "matches": matches,
        }


    async def generate_report(self, chain: List[RedirectionNode]) -> str:
        """
        Generates a summary report using Ollama based on the redirection chain.
        """
        chain_desc = "\n".join([
            f"Step {node.step}: {node.url} (Status: {node.status})\n"
            f"  - CTI Verdict: {node.cti_data.get('verdict', 'Unknown') if node.cti_data else 'Unknown'}\n"
            f"  - CTI Data: {node.cti_data}\n"
            f"  - Extracted Links Count: {len(node.extracted_links) if node.extracted_links else 0}"
            for node in chain
        ])
        
        prompt = f"""
        Analyze the following URL redirection chain and CTI data.
        
        Data:
        {chain_desc}
        
        IMPORTANT RULES:
        1. **TRUST CTI DATA**: If ANY node has 'malicious' count > 0 or verdict='Malicious', you MUST report it as MALICIOUS in the VirusTotal Result section.
        2. **EXACT NUMBERS**: Report the EXACT numbers from the stats (e.g., "5/90 vendors flagged this...").
        3. **NO HALLUCINATION**: If CTI Data is empty/None, strictly say "No VirusTotal data available". Do NOT assume it is Clean.
        
        Please provide a report in the following STRICT format:
        
        ## VirusTotal Result
        (Current Status: [MALICIOUS / SUSPICIOUS / CLEAN / UNKNOWN])
        (Report EXACT malicious/suspicious/harmless stats from the data. Highlight if malicious > 0.)
        
        ## Domain Intelligence
        (Summarize Domain Age and Registrar info. Highlight if the domain is suspiciously new (< 30 days).)
        
        ## Malicious Code Explanation
        (If any malicious indicators were found in code or CTI, explain them here. Otherwise, state 'No malicious code found'.)
        """
        
        try:
            response = await self.client.chat(model=self.model_name, messages=[
                {'role': 'user', 'content': prompt},
            ])
            return response.message.content
        except Exception as e:
            return f"Error generating AI report: {str(e)}. Check URL: {OLLAMA_API_URL}"

    async def analyze_code(self, html_content: str, headers: dict) -> str:
        """
        Performs a code-level security analysis using Ollama,
        enhanced with the malicious code pattern dataset.
        """
        # Step 1: Pre-scan the HTML against our pattern dataset
        pattern_matches = self._scan_patterns(html_content)
        
        # Step 2: Build the dataset-aware section for the prompt
        if pattern_matches:
            match_section = "## ⚠️ DATASET PATTERN MATCHES FOUND\n"
            match_section += f"The following {len(pattern_matches)} known malicious patterns were detected:\n\n"
            for m in pattern_matches:
                match_section += (
                    f"- **[ID:{m['id']}] {m['type']} / {m['category']}**: {m['description']}\n"
                    f"  Matched keywords: `{', '.join(m['matched_patterns'])}`\n"
                )
                if m.get("example"):
                    match_section += f"  Known example: `{m['example']}`\n"
            match_section += "\nYou MUST incorporate these matches into your analysis. These are CONFIRMED pattern matches from our threat intelligence dataset.\n"
        else:
            match_section = "## Dataset Pattern Scan\nNo known malicious patterns from our threat intelligence dataset were matched.\n"
        
        # Step 3: Build the full dataset category reference
        dataset_ref = self._build_dataset_reference()
        
        prompt = f"""
        You are a cybersecurity malware analyst. Perform a comprehensive security analysis on the following HTML content and HTTP headers.

        ## THREAT INTELLIGENCE DATASET
        You have access to a curated threat intelligence dataset with {len(self.mal_patterns)} known malicious code signatures.
        Categories to look for:
        {dataset_ref}

        {match_section}

        ## ANALYSIS INSTRUCTIONS
        Focus on BEHAVIORAL and CONTEXTUAL signals, not just syntax. Look for:
        1. **Fake Interaction Gates**: Client-side-only CAPTCHAs, fake "security check" spinners, "processing" animations, or "verification" gates that don't perform real server validation.
        2. **Deceptive Forms**: Hidden forms/inputs used without user awareness, non-semantic/randomized field IDs, or JavaScript-triggered submissions without explicit user intent.
        3. **Visual Trust Theater**: Use of security language ("Secure", "Verified"), icons (padlocks, shields), or branding without underlying security implementation.
        4. **Phishing Mechanics**: Techniques common in phishing kits, such as session relay indicators, detailed UI replication of legitimate services, or immediate data exfiltration attempts.
        5. **Obfuscation**: eval(), atob(), String.fromCharCode(), hex encoding, ROT13, or variable renaming obfuscation (_0x patterns).
        6. **Data Exfiltration**: Cookie theft, keyloggers, form grabbers, beacon-based exfiltration.
        7. **Crypto/Financial**: Credit card skimmers (Magecart), crypto wallet stealers, formjacking.

        ## HTTP Headers
        {headers}
        
        ## HTML Content (Truncated to 4000 chars)
        {html_content[:4000]}
        
        ## OUTPUT FORMAT (Markdown)
        
        ### 1. Dataset Match Summary
        (List which threat intelligence patterns were matched and their severity. If none, say "No dataset matches.")
        
        ### 2. Security & Behavioral Summary
        (A concise summary of the page's purpose and any suspicious behavior found.)

        ### 3. Detected Threat Indicators
        (List specific behavioral patterns found. Reference dataset IDs where applicable. If none, say "No behavioral threats detected".)

        ### 4. Detailed Technical Analysis
        - **Malicious Code/Patterns**: (Paste specific code snippets or describe the mechanism)
        - **Trust Theater**: (Describe any fake security elements)
        - **Form/Input Behavior**: (Analyze hidden or deceptive inputs)
        - **Obfuscation Techniques**: (Any code obfuscation found)
        
        ### 5. Final Verdict
        (Safe / Suspicious / Malicious - with clear reasoning based on dataset matches AND behavioral evidence)
        """
        try:
            response = await self.client.chat(model=self.model_name, messages=[
                {'role': 'user', 'content': prompt},
            ])
            return response.message.content
        except Exception as e:
            return f"Error analyzing code: {str(e)}"
