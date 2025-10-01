"""
Web Scraper for Research Paper Abstracts
Extracts full abstracts from paper URLs with fallback to snippets
"""

import logging
from typing import Optional, Dict
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScraperError(Exception):
    """Custom exception for scraping errors"""
    pass


class PaperScraper:
    """Scraper for extracting abstracts from research paper URLs"""
    
    def __init__(self, timeout: int = 10):
        """
        Initialize scraper
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(requests.RequestException),
        reraise=True
    )
    def _fetch_page(self, url: str) -> str:
        """
        Fetch page content with retry logic
        
        Args:
            url: URL to fetch
            
        Returns:
            Page HTML content
            
        Raises:
            requests.RequestException: If fetch fails after retries
        """
        logger.info(f"Fetching: {url}")
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        return response.text
    
    def scrape_abstract(self, url: str, fallback_snippet: str = "") -> Dict[str, str]:
        """
        Scrape abstract from paper URL with fallback to snippet
        
        Args:
            url: Paper URL
            fallback_snippet: Snippet to use if scraping fails
            
        Returns:
            Dictionary with:
                - abstract: Full abstract or snippet
                - source: 'scraped' or 'snippet'
                - success: Boolean indicating if scraping succeeded
        """
        try:
            # Parse domain to determine scraping strategy
            domain = urlparse(url).netloc.lower()
            
            logger.info(f"Scraping abstract from: {domain}")
            
            # Try domain-specific scrapers
            if 'arxiv.org' in domain:
                abstract = self._scrape_arxiv(url)
            elif 'pubmed' in domain or 'ncbi.nlm.nih.gov' in domain:
                abstract = self._scrape_pubmed(url)
            elif 'ieee' in domain:
                abstract = self._scrape_ieee(url)
            elif 'acm.org' in domain:
                abstract = self._scrape_acm(url)
            elif 'springer' in domain:
                abstract = self._scrape_springer(url)
            else:
                # Generic scraper for other sites
                abstract = self._scrape_generic(url)
            
            if abstract and len(abstract.strip()) > 50:
                logger.info(f"Successfully scraped abstract ({len(abstract)} chars)")
                return {
                    'abstract': abstract.strip(),
                    'source': 'scraped',
                    'success': True
                }
            else:
                logger.warning("Scraped abstract too short, using fallback")
                raise ScraperError("Abstract too short")
                
        except Exception as e:
            logger.warning(f"Scraping failed: {e}. Using fallback snippet.")
            return {
                'abstract': fallback_snippet,
                'source': 'snippet',
                'success': False
            }
    
    def _scrape_arxiv(self, url: str) -> Optional[str]:
        """Scrape abstract from arXiv"""
        try:
            html = self._fetch_page(url)
            soup = BeautifulSoup(html, 'lxml')
            
            # arXiv abstract is in blockquote with class 'abstract'
            abstract_elem = soup.find('blockquote', class_='abstract')
            if abstract_elem:
                # Remove the "Abstract:" label
                text = abstract_elem.get_text(strip=True)
                return text.replace('Abstract:', '').strip()
            
            return None
        except Exception as e:
            logger.error(f"arXiv scraping error: {e}")
            return None
    
    def _scrape_pubmed(self, url: str) -> Optional[str]:
        """Scrape abstract from PubMed"""
        try:
            html = self._fetch_page(url)
            soup = BeautifulSoup(html, 'lxml')
            
            # PubMed abstract is in div with class 'abstract-content'
            abstract_elem = soup.find('div', class_='abstract-content')
            if not abstract_elem:
                # Try alternative selector
                abstract_elem = soup.find('div', id='abstract')
            
            if abstract_elem:
                return abstract_elem.get_text(strip=True)
            
            return None
        except Exception as e:
            logger.error(f"PubMed scraping error: {e}")
            return None
    
    def _scrape_ieee(self, url: str) -> Optional[str]:
        """Scrape abstract from IEEE"""
        try:
            html = self._fetch_page(url)
            soup = BeautifulSoup(html, 'lxml')
            
            # IEEE abstract is in div with class 'abstract-text'
            abstract_elem = soup.find('div', class_='abstract-text')
            if not abstract_elem:
                # Try alternative
                abstract_elem = soup.find('div', {'class': 'u-mb-1'})
            
            if abstract_elem:
                return abstract_elem.get_text(strip=True)
            
            return None
        except Exception as e:
            logger.error(f"IEEE scraping error: {e}")
            return None
    
    def _scrape_acm(self, url: str) -> Optional[str]:
        """Scrape abstract from ACM Digital Library"""
        try:
            html = self._fetch_page(url)
            soup = BeautifulSoup(html, 'lxml')
            
            # ACM abstract
            abstract_elem = soup.find('div', class_='abstractSection')
            if not abstract_elem:
                abstract_elem = soup.find('div', {'role': 'paragraph'})
            
            if abstract_elem:
                return abstract_elem.get_text(strip=True)
            
            return None
        except Exception as e:
            logger.error(f"ACM scraping error: {e}")
            return None
    
    def _scrape_springer(self, url: str) -> Optional[str]:
        """Scrape abstract from Springer"""
        try:
            html = self._fetch_page(url)
            soup = BeautifulSoup(html, 'lxml')
            
            # Springer abstract
            abstract_elem = soup.find('div', class_='c-article-section__content')
            if not abstract_elem:
                abstract_elem = soup.find('section', {'data-title': 'Abstract'})
            
            if abstract_elem:
                return abstract_elem.get_text(strip=True)
            
            return None
        except Exception as e:
            logger.error(f"Springer scraping error: {e}")
            return None
    
    def _scrape_generic(self, url: str) -> Optional[str]:
        """Generic scraper for unknown sites"""
        try:
            html = self._fetch_page(url)
            soup = BeautifulSoup(html, 'lxml')
            
            # Try common abstract selectors
            selectors = [
                ('meta', {'name': 'description'}),
                ('meta', {'property': 'og:description'}),
                ('div', {'class': 'abstract'}),
                ('section', {'id': 'abstract'}),
                ('div', {'id': 'abstract'}),
                ('p', {'class': 'abstract'}),
            ]
            
            for tag, attrs in selectors:
                elem = soup.find(tag, attrs)
                if elem:
                    if tag == 'meta':
                        content = elem.get('content', '')
                    else:
                        content = elem.get_text(strip=True)
                    
                    if content and len(content) > 50:
                        return content
            
            return None
        except Exception as e:
            logger.error(f"Generic scraping error: {e}")
            return None
    
    def batch_scrape(self, papers: list) -> list:
        """
        Scrape abstracts for multiple papers
        
        Args:
            papers: List of paper dictionaries with 'link' and 'snippet' keys
            
        Returns:
            Updated list of papers with 'abstract', 'abstract_source', and 'scrape_success' keys
        """
        logger.info(f"Batch scraping {len(papers)} papers")
        
        for i, paper in enumerate(papers):
            logger.info(f"Processing paper {i+1}/{len(papers)}")
            
            result = self.scrape_abstract(
                url=paper.get('link', ''),
                fallback_snippet=paper.get('snippet', '')
            )
            
            paper['abstract'] = result['abstract']
            paper['abstract_source'] = result['source']
            paper['scrape_success'] = result['success']
        
        success_count = sum(1 for p in papers if p.get('scrape_success'))
        logger.info(f"Successfully scraped {success_count}/{len(papers)} abstracts")
        
        return papers


# Example usage
if __name__ == "__main__":
    scraper = PaperScraper()
    
    # Test with arXiv paper
    test_url = "https://arxiv.org/abs/1706.03762"  # "Attention is All You Need"
    result = scraper.scrape_abstract(test_url, fallback_snippet="Transformer architecture paper")
    
    print(f"\nSource: {result['source']}")
    print(f"Success: {result['success']}")
    print(f"Abstract: {result['abstract'][:200]}...")
