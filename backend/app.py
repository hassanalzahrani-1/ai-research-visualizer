"""
FastAPI Backend for AI Research Paper Visualizer
Integrates Serper API, web scraping, and Scenario API
"""

import json
import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from .serper_client import SerperClient
from .scenario_client import ScenarioClient
from .scraper import PaperScraper
from .models import (
    ProcessPapersRequest,
    ProcessPapersResponse,
    ProcessedPaper,
    GenerateImageRequest,
    GenerateImageResponse
)

# Configure logging with colors
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Research Visualizer API",
    description="Search Google Scholar, scrape abstracts, and generate visual representations of research papers",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_serper_client() -> SerperClient:
    """Get Serper client"""
    try:
        return SerperClient()
    except Exception as e:
        logger.error(f"Failed to initialize Serper API: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Serper API not configured"
        )


def get_scenario_client() -> ScenarioClient:
    """Get Scenario client"""
    try:
        return ScenarioClient()
    except Exception as e:
        logger.error(f"Failed to initialize Scenario API: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Scenario API not configured"
        )


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Research Visualizer",
        "version": "1.0.0"
    }


@app.post("/api/process", response_model=ProcessPapersResponse)
async def process_papers(request: ProcessPapersRequest):
    """
    Fast pipeline: Search papers and return immediately (no image generation)
    Images can be loaded progressively via /api/generate-image endpoint
    """
    try:
        logger.info(f"Processing papers for query: {request.query}")
        logger.info(f"Request params - num_papers: {request.num_papers}")
        
        # Step 1: Search with Serper API (fast!)
        logger.info("=" * 60)
        logger.info("SERPER API - SEARCHING PAPERS")
        logger.info("=" * 60)
        serper = get_serper_client()
        papers = serper.search_scholar(
            query=request.query,
            num_results=request.num_papers
        )
        
        logger.info(f"Found {len(papers)} papers")
        
        # Step 2: Scrape abstracts from paper URLs
        logger.info("\n" + "=" * 60)
        logger.info("WEB SCRAPER - EXTRACTING ABSTRACTS")
        logger.info("=" * 60)
        scraper = PaperScraper()
        scraped_papers = scraper.scrape_papers(papers)
        
        logger.info(f"Scraped {len(scraped_papers)} papers")
        
        # Step 3: Convert to ProcessedPaper objects
        processed_papers = [
            ProcessedPaper(
                title=paper['title'],
                link=paper['link'],
                snippet=paper['snippet'],
                year=paper.get('year'),
                abstract=paper.get('abstract'),
                image_urls=[]  # Empty - will be loaded progressively
            )
            for paper in scraped_papers
        ]
        
        return ProcessPapersResponse(
            query=request.query,
            papers=processed_papers
        )
        
    except Exception as e:
        import traceback
        logger.error(f"Pipeline error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline error: {str(e)}"
        )


@app.post("/api/generate-image", response_model=GenerateImageResponse)
async def generate_image(request: GenerateImageRequest):
    """
    Generate image for a single paper (called progressively by frontend)
    """
    try:
        paper = request.paper
        logger.info("=" * 60)
        logger.info("SCENARIO API - GENERATING IMAGE")
        logger.info("=" * 60)
        logger.info(f"Paper: {paper.title[:50]}...")
        
        scenario = get_scenario_client()
        
        # Prepare paper data for image generation
        paper_dict = paper.model_dump()
        
        # Truncate abstract for faster image generation (keep first 500 chars)
        if paper_dict.get('abstract') and len(paper_dict['abstract']) > 500:
            paper_dict['abstract'] = paper_dict['abstract'][:500] + "..."
        
        # CRITICAL: Remove snippet to prevent query contamination
        # The snippet field may contain search-highlighted text that leaks user query terms
        paper_dict.pop('snippet', None)
        
        # Also remove fields not needed for image generation
        paper_dict.pop('image_urls', None)
        paper_dict.pop('link', None)
        
        paper_json = json.dumps(paper_dict, indent=2)
        
        # Build prompt with only title, abstract, and year
        prompt = f"""Create an engaging, informative scientific visualization that captures the essence of this research paper.
        Paper Data:
        {paper_json}

        Style: Modern, professional scientific illustration with clean design.
        Goal: Grab reader attention and convey the research's key concepts visually.
        Make it informative, insightful, and visually compelling for academic audiences."""
            
        logger.info(f"Generated prompt length: {len(prompt)} characters")
        logger.info(f"Paper data sent to Scenario: title={paper_dict.get('title', 'N/A')[:50]}..., has_abstract={bool(paper_dict.get('abstract'))}")
        
        image_urls = scenario.generate_image(
            prompt=prompt,
            width=1024,
            height=1024,
            samples=1
        )
        
        return GenerateImageResponse(
            image_urls=image_urls,
            success=True
        )
        
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        return GenerateImageResponse(
            image_urls=[],
            success=False
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
