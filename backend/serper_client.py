"""
Serper API Client for Google Scholar Search
Implements error handling and retry logic with exponential backoff
"""

import os
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import requests
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SerperAPIError(Exception):
    """Custom exception for Serper API errors"""
    pass


class SerperClient:
    """Client for interacting with Serper API for Google Scholar searches"""
    
    BASE_URL = "https://google.serper.dev/scholar"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Serper API client
        
        Args:
            api_key: Serper API key (defaults to SERPER_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('SERPER_API_KEY')
        if not self.api_key:
            raise ValueError("SERPER_API_KEY not found in environment variables")
        
        self.headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.RequestException, SerperAPIError)),
        reraise=True
    )
    def _make_request(self, payload: Dict) -> Dict:
        """
        Make API request with retry logic
        
        Args:
            payload: Request payload
            
        Returns:
            API response as dictionary
            
        Raises:
            SerperAPIError: If API request fails after retries
        """
        try:
            logger.info(f"Making Serper API request: {payload.get('q', 'N/A')}")
            response = requests.post(
                self.BASE_URL,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            raise SerperAPIError(f"API request failed: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            raise SerperAPIError(f"Network error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise SerperAPIError(f"Unexpected error: {e}")
    
    def search_scholar(
        self,
        query: str,
        num_results: int = 10,
        date_range: Optional[str] = None
    ) -> List[Dict]:
        """
        Search Google Scholar for research papers
        
        Args:
            query: Search query (e.g., "Artificial Intelligence")
            num_results: Number of results to return (default: 10)
            date_range: Date range filter - 'week', 'month', 'year', or None
            
        Returns:
            List of paper dictionaries with keys:
                - title: Paper title
                - link: URL to paper
                - snippet: Abstract snippet
                - publication_info: Journal/conference info
                - cited_by: Citation count
                - year: Publication year
                
        Raises:
            SerperAPIError: If search fails
        """
        payload = {
            'q': query,
            'num': num_results
        }
        
        # Add date range if specified
        if date_range:
            date_filters = {
                'week': 'w',
                'month': 'm',
                'year': 'y'
            }
            if date_range.lower() in date_filters:
                payload['tbs'] = f"qdr:{date_filters[date_range.lower()]}"
        
        try:
            response = self._make_request(payload)
            papers = self._parse_response(response)
            logger.info(f"Successfully retrieved {len(papers)} papers")
            return papers
            
        except SerperAPIError as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def _parse_response(self, response: Dict) -> List[Dict]:
        """
        Parse Serper API response into structured paper data
        
        Args:
            response: Raw API response
            
        Returns:
            List of parsed paper dictionaries
        """
        papers = []
        organic_results = response.get('organic', [])
        
        for result in organic_results:
            paper = {
                'title': result.get('title', 'N/A'),
                'link': result.get('link', ''),
                'snippet': result.get('snippet', ''),
                'publication_info': result.get('publicationInfo', {}).get('summary', 'N/A'),
                'cited_by': self._extract_citations(result),
                'year': self._extract_year(result),
                'authors': self._extract_authors(result)
            }
            papers.append(paper)
        
        return papers
    
    def _extract_citations(self, result: Dict) -> int:
        """Extract citation count from result"""
        inline_links = result.get('inlineLinks', [])
        for link in inline_links:
            if 'Cited by' in link.get('title', ''):
                # Extract number from "Cited by 123"
                try:
                    return int(''.join(filter(str.isdigit, link.get('title', '0'))))
                except ValueError:
                    return 0
        return 0
    
    def _extract_year(self, result: Dict) -> Optional[int]:
        """Extract publication year from result"""
        pub_info = result.get('publicationInfo', {}).get('summary', '')
        # Try to extract 4-digit year
        import re
        year_match = re.search(r'\b(19|20)\d{2}\b', pub_info)
        if year_match:
            return int(year_match.group())
        return None
    
    def _extract_authors(self, result: Dict) -> str:
        """Extract authors from result"""
        pub_info = result.get('publicationInfo', {}).get('summary', '')
        # Authors are typically before the year
        parts = pub_info.split('-')
        if parts:
            return parts[0].strip()
        return 'N/A'


# Example usage
if __name__ == "__main__":
    try:
        client = SerperClient()
        papers = client.search_scholar(
            query="Artificial Intelligence",
            num_results=5,
            date_range="month"
        )
        
        print(f"\nFound {len(papers)} papers:\n")
        for i, paper in enumerate(papers, 1):
            print(f"{i}. {paper['title']}")
            print(f"   Authors: {paper['authors']}")
            print(f"   Year: {paper['year']}")
            print(f"   Citations: {paper['cited_by']}")
            print(f"   Link: {paper['link']}")
            print(f"   Snippet: {paper['snippet'][:100]}...")
            print()
            
    except Exception as e:
        print(f"Error: {e}")
