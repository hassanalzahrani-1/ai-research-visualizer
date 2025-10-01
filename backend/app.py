"""
FastAPI Backend for AI Research Paper Visualizer
Integrates Serper API, web scraping, and Scenario API
"""

import json
import logging
from pathlib import Path
from typing import List
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.models import (
    SearchRequest, SearchResponse, PaperResponse,
    GenerateImageRequest, GenerateImageResponse,
    ProcessPapersRequest, ProcessPapersResponse, ProcessedPaper,
    HealthResponse
)
from backend.serper_client import SerperClient, SerperAPIError
from backend.scenario_client import ScenarioClient, ScenarioAPIError
from backend.scraper import PaperScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Research Paper Visualizer API",
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

# Mount static files for images
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)
app.mount("/images", StaticFiles(directory=str(output_dir)), name="images")

# Initialize clients
serper_client = None
scenario_client = None
scraper = PaperScraper()

# Last result cache
LAST_RESULT_FILE = output_dir / "last_result.json"


def get_serper_client() -> SerperClient:
    """Get or create Serper client"""
    global serper_client
    if serper_client is None:
        try:
            serper_client = SerperClient()
        except Exception as e:
            logger.error(f"Failed to initialize Serper client: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Serper API not configured"
            )
    return serper_client


def get_scenario_client() -> ScenarioClient:
    """Get or create Scenario client"""
    global scenario_client
    if scenario_client is None:
        try:
            scenario_client = ScenarioClient(output_dir=str(output_dir))
        except Exception as e:
            logger.error(f"Failed to initialize Scenario client: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Scenario API not configured"
            )
    return scenario_client


def save_last_result(data: dict):
    """Save last result to file"""
    try:
        with open(LAST_RESULT_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save last result: {e}")


def load_last_result() -> dict:
    """Load last result from file"""
    try:
        if LAST_RESULT_FILE.exists():
            with open(LAST_RESULT_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load last result: {e}")
    return None


@app.get("/", response_class=FileResponse)
async def root():
    """Serve frontend"""
    # Will serve React app in production
    return {"message": "AI Research Paper Visualizer API", "docs": "/api/docs"}


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    services = {
        "serper": "unknown",
        "scenario": "unknown",
        "scraper": "ok"
    }
    
    try:
        get_serper_client()
        services["serper"] = "ok"
    except:
        services["serper"] = "error"
    
    try:
        get_scenario_client()
        services["scenario"] = "ok"
    except:
        services["scenario"] = "error"
    
    return HealthResponse(
        status="healthy" if all(v == "ok" for v in services.values()) else "degraded",
        version="1.0.0",
        services=services
    )


@app.post("/api/search", response_model=SearchResponse)
async def search_papers(request: SearchRequest):
    """
    Search Google Scholar for research papers
    """
    try:
        client = get_serper_client()
        papers = client.search_scholar(
            query=request.query,
            num_results=request.num_results,
            date_range=request.date_range
        )
        
        return SearchResponse(
            query=request.query,
            num_results=len(papers),
            papers=[PaperResponse(**paper) for paper in papers]
        )
        
    except SerperAPIError as e:
        logger.error(f"Serper API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Search service error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/api/scrape")
async def scrape_abstracts(papers: List[PaperResponse]):
    """
    Scrape full abstracts from paper URLs
    """
    try:
        papers_dict = [paper.model_dump() for paper in papers]
        scraped_papers = scraper.batch_scrape(papers_dict)
        
        return {
            "total": len(scraped_papers),
            "successful_scrapes": sum(1 for p in scraped_papers if p.get('scrape_success')),
            "papers": scraped_papers
        }
        
    except Exception as e:
        logger.error(f"Scraping error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scraping error: {str(e)}"
        )


@app.post("/api/generate-image", response_model=GenerateImageResponse)
async def generate_image(request: GenerateImageRequest):
    """
    Generate image from paper title and abstract
    """
    try:
        client = get_scenario_client()
        
        # Create prompt from title and abstract
        prompt = f"Scientific visualization of: {request.title}. {request.abstract[:200]}"
        
        image_paths = client.generate_image(
            prompt=prompt,
            width=request.width,
            height=request.height,
            samples=1
        )
        
        return GenerateImageResponse(
            title=request.title,
            image_paths=image_paths,
            success=len(image_paths) > 0
        )
        
    except ScenarioAPIError as e:
        logger.error(f"Scenario API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Image generation service error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in image generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/api/process", response_model=ProcessPapersResponse)
async def process_papers(request: ProcessPapersRequest):
    """
    Full pipeline: Search -> Scrape -> Generate Images
    """
    try:
        logger.info(f"Processing papers for query: {request.query}")
        
        # Step 1: Search
        serper = get_serper_client()
        papers = serper.search_scholar(
            query=request.query,
            num_results=request.num_papers,
            date_range=request.date_range
        )
        
        logger.info(f"Found {len(papers)} papers")
        
        # Step 2: Scrape abstracts
        papers = scraper.batch_scrape(papers)
        
        # Step 3: Generate images (if requested)
        processed_papers = []
        successful = 0
        
        for paper in papers:
            try:
                image_paths = []
                
                # Get abstract text safely
                abstract_text = paper.get('abstract') or paper.get('snippet', '')
                
                if request.generate_images:
                    scenario = get_scenario_client()
                    prompt = f"Scientific visualization of: {paper.get('title', 'Research Paper')}. {abstract_text[:200]}"
                    
                    image_paths = scenario.generate_image(
                        prompt=prompt,
                        width=1024,
                        height=1024,
                        samples=1
                    )
                
                processed_papers.append(ProcessedPaper(
                    title=paper.get('title', 'Unknown Title'),
                    link=paper.get('link', ''),
                    abstract=abstract_text,
                    abstract_source=paper.get('abstract_source', 'snippet'),
                    publication_info=paper.get('publication_info', 'N/A'),
                    cited_by=paper.get('cited_by', 0),
                    year=paper.get('year'),
                    authors=paper.get('authors', 'N/A'),
                    image_paths=image_paths,
                    processing_success=True
                ))
                successful += 1
                
            except Exception as e:
                logger.error(f"Error processing paper '{paper.get('title', 'Unknown')}': {e}")
                # Get abstract safely for error case too
                abstract_text = paper.get('abstract') or paper.get('snippet', '')
                processed_papers.append(ProcessedPaper(
                    title=paper.get('title', 'Unknown Title'),
                    link=paper.get('link', ''),
                    abstract=abstract_text,
                    abstract_source=paper.get('abstract_source', 'snippet'),
                    publication_info=paper.get('publication_info', 'N/A'),
                    cited_by=paper.get('cited_by', 0),
                    year=paper.get('year'),
                    authors=paper.get('authors', 'N/A'),
                    image_paths=[],
                    processing_success=False
                ))
        
        response = ProcessPapersResponse(
            query=request.query,
            total_papers=len(processed_papers),
            successful=successful,
            papers=processed_papers
        )
        
        # Save as last result
        save_last_result(response.model_dump())
        
        return response
        
    except Exception as e:
        import traceback
        logger.error(f"Pipeline error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline error: {str(e)}"
        )


@app.get("/api/last-result")
async def get_last_result():
    """Get the last processed result"""
    result = load_last_result()
    if result:
        return result
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No previous results found"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
