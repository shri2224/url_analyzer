from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.schemas import UrlRequest, AnalysisReport, RedirectionNode
from app.modules.browser_agent import BrowserAgent
from app.modules.cti_checker import CTIChecker
from app.modules.reporter import Reporter
import traceback

router = APIRouter()

# Initialize modules
# In a real app, these might be dependencies or singletons
browser_agent = BrowserAgent()
cti_checker = CTIChecker()
reporter = Reporter()

@router.post("/analyze", response_model=AnalysisReport)
async def analyze_url(request: UrlRequest):
    try:
        # Configuration for recursion
        MAX_DEPTH = 1 # Depth 0 = Entry, Depth 1 = Links on Entry Page
        MAX_LINKS_PER_PAGE = 3
        
        # DFS/BFS Helper
        async def process_url(url: str, depth: int) -> AnalysisReport:
            print(f"Analyzing: {url} (Depth: {depth})")
            
            # 1. Trace
            chain = await browser_agent.trace(url)
            
            # 2. Enrich Nodes (CTI + Code Analysis)
            for node in chain:
                # CTI
                node.cti_data = await cti_checker.check_url(node.url)
                
                # Code Analysis (on final node or if body exists)
                if node.body_summary:
                    node.code_analysis_verdict = await reporter.analyze_code(node.body_summary, node.headers)

            final_node = chain[-1] if chain else None
            final_url = final_node.url if final_node else url
            
            # 3. Recursion: Identify Links to Follow
            children_reports = []
            if depth < MAX_DEPTH and final_node and final_node.extracted_links:
                # Filter/Limit links to avoid explosion
                links_to_visit = final_node.extracted_links[:MAX_LINKS_PER_PAGE]
                
                for link in links_to_visit:
                    # Basic validation or filtering (same domain? or all?)
                    if link.startswith("http"):
                        child_report = await process_url(link, depth + 1)
                        children_reports.append(child_report)

            # 4. Generate Summary for this level
            summary = await reporter.generate_report(chain)
            
            return AnalysisReport(
                original_url=url,
                final_url=final_url,
                chain=chain,
                summary_report=summary,
                children=children_reports
            )

        # Start Analysis
        report = await process_url(request.url, 0)
        return report

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
