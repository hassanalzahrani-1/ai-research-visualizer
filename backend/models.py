"""
Pydantic models for API request/response validation
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ProcessPapersRequest(BaseModel):
    """Request model for full pipeline"""
    query: str = Field(..., description="Search query")
    num_papers: int = Field(5, ge=1, le=20, description="Number of papers to process")


class ProcessedPaper(BaseModel):
    """Model for a fully processed paper"""
    title: str
    link: str
    snippet: str
    year: Optional[int]
    abstract: Optional[str] = None  # Scraped abstract (None if scraping failed)
    image_urls: List[str] = []  # Direct URLs from Scenario API


class ProcessPapersResponse(BaseModel):
    """Response model for full pipeline"""
    query: str
    papers: List[ProcessedPaper]


class GenerateImageRequest(BaseModel):
    """Request model for generating image for a single paper"""
    paper: ProcessedPaper = Field(..., description="Full paper object with all fields")


class GenerateImageResponse(BaseModel):
    """Response model for image generation"""
    image_urls: List[str]
    success: bool