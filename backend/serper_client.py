"""
Serper API Client for Google Scholar Search
Implements error handling and retry logic with exponential backoff
"""

import os
import re
import logging
from typing import Dict, List, Optional
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

# Get logger (don't configure - let app.py handle it)
logger = logging.getLogger(__name__)


class SerperAPIError(Exception):
    """Custom exception for Serper API errors"""
    pass


class SerperClient:
    """Client for interacting with Serper API for Google Scholar searches"""
    
    BASE_URL = "https://google.serper.dev/scholar"
    
    # Translation table for cleaning snippets (created once)
    _SNIPPET_TRANSLATION = str.maketrans({
        '…': ' ',
        '\u2026': ' ',  # Unicode ellipsis
        '\u2019': "'",  # Right single quotation mark
        '\u2018': "'",  # Left single quotation mark
        '\u201c': '"',  # Left double quotation mark
        '\u201d': '"',  # Right double quotation mark
        '\u2013': '-',  # En dash
        '\u2014': '-',  # Em dash
    })
    
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
        num_results: int = 10
    ) -> List[Dict]:
        """
        Search Google Scholar for research papers
        
        Args:
            query: Search query (e.g., "Artificial Intelligence")
            num_results: Number of results to return (default: 10)
            
        Returns:
            List of paper dictionaries with keys:
                - title: Paper title
                - link: URL to paper
                - snippet: Abstract snippet
                - year: Publication year
                
        Raises:
            SerperAPIError: If search fails
        """
        # Use Google Scholar's 'as_ylo' parameter to filter by year
        # as_ylo = "as year low" - minimum year for results
        min_year = 2025
        
        # Add site restrictions to only get papers from scrapable sources
        site_filter = "(site:arxiv.org OR site:pubmed.ncbi.nlm.nih.gov OR site:researchgate.net)"
        enhanced_query = f"{site_filter} {query}"
        
        payload = {
            'q': enhanced_query,
            'num': num_results * 2,  # Request extra to ensure enough results
            'page': 1,
            'gl': 'us',  # Country - US for English results
            'hl': 'en',  # Language - English
            'as_ylo': min_year  # Filter for papers from 2025 onwards
        }
        
        logger.info(f"Searching for papers from {min_year} onwards")
        
        try:
            # Make API request
            response = self._make_request(payload)
            
            # Parse response
            papers = self._parse_response(response)
            
            logger.info(f"Retrieved {len(papers)} papers from API")
            
            # Limit to requested number of results
            papers = papers[:num_results]
            
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
            # Get ONLY the basic snippet (no highlighted or rich snippets)
            # This prevents user query terms from contaminating the paper data
            snippet = result.get('snippet', '')
            
            # Clean up snippet - remove ellipses and extra spaces
            snippet = self._clean_snippet(snippet)
            
            paper = {
                'title': self._clean_snippet(result.get('title', 'N/A')),
                'link': result.get('link', ''),
                'snippet': snippet,
                'year': self._extract_year(result),
            }
            papers.append(paper)
        
        return papers
    
    def _clean_snippet(self, snippet: str) -> str:
        """Clean snippet text by removing ellipses, unicode characters, and extra spaces"""
        if not snippet:
            return snippet
        
        # Use pre-built translation table for faster processing
        snippet = snippet.translate(self._SNIPPET_TRANSLATION)
        snippet = snippet.replace('...', ' ')  # Regular ellipsis
        
        # Remove extra whitespace and return
        return ' '.join(snippet.split())
    
    def _extract_year(self, result: Dict) -> Optional[int]:
        """Extract publication year from result"""
        pub_info = result.get('publicationInfo', {})
        if isinstance(pub_info, dict):
            pub_info_str = pub_info.get('summary', '')
        else:
            pub_info_str = pub_info if pub_info else ''
        
        # Try to extract 4-digit year
        year_match = re.search(r'\b(19|20)\d{2}\b', pub_info_str)
        if year_match:
            return int(year_match.group())
        return None
    
# Example usage
if __name__ == "__main__":
    try:
        client = SerperClient()
        papers = client.search_scholar(
            query="Artificial Intelligence",
            num_results=5
        )
        
        print(f"\nFound {len(papers)} papers:\n")
        for i, paper in enumerate(papers, 1):
            print(f"{i}. {paper['title']}")
            print(f"   Year: {paper['year']}")
            print(f"   Link: {paper['link']}")
            print(f"   Snippet: {paper['snippet'][:100]}...")
            print()
            
    except Exception as e:
        print(f"Error: {e}")
