"""
Pydantic models for API request/response validation
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Request model for paper search"""
    query: str = Field(..., description="Search query (e.g., 'Artificial Intelligence')")
    num_results: int = Field(10, ge=1, le=50, description="Number of results to return")
    date_range: Optional[str] = Field(None, description="Date range filter: 'week', 'month', 'year'")


class PaperResponse(BaseModel):
    """Response model for a single paper"""
    title: str
    link: str
    snippet: str
    abstract: Optional[str] = None
    abstract_source: Optional[str] = None
    scrape_success: Optional[bool] = None
    publication_info: str
    cited_by: int
    year: Optional[int]
    authors: str
    image_url: Optional[str] = None


class SearchResponse(BaseModel):
    """Response model for search results"""
    query: str
    num_results: int
    papers: List[PaperResponse]


class GenerateImageRequest(BaseModel):
    """Request model for image generation"""
    title: str = Field(..., description="Paper title")
    abstract: str = Field(..., description="Paper abstract or snippet")
    width: int = Field(1024, ge=512, le=2048)
    height: int = Field(1024, ge=512, le=2048)


class GenerateImageResponse(BaseModel):
    """Response model for image generation"""
    title: str
    image_paths: List[str]
    success: bool


class ProcessPapersRequest(BaseModel):
    """Request model for full pipeline"""
    query: str = Field(..., description="Search query")
    num_papers: int = Field(5, ge=1, le=20, description="Number of papers to process")
    date_range: Optional[str] = Field(None, description="Date range filter")
    generate_images: bool = Field(True, description="Whether to generate images")


class ProcessedPaper(BaseModel):
    """Model for a fully processed paper"""
    title: str
    link: str
    abstract: str
    abstract_source: str
    publication_info: str
    cited_by: int
    year: Optional[int]
    authors: str
    image_paths: List[str] = []
    processing_success: bool


class ProcessPapersResponse(BaseModel):
    """Response model for full pipeline"""
    query: str
    total_papers: int
    successful: int
    papers: List[ProcessedPaper]


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    services: dict
