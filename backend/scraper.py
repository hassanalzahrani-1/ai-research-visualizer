"""
Web Scraper for Research Papers
Extracts abstracts from academic sources
"""

import logging
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from typing import Optional, Dict
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

# Get logger
logger = logging.getLogger(__name__)


class ScraperError(Exception):
    """Custom exception for scraping errors"""
    pass


class PaperScraper:
    """Scraper for extracting abstracts from academic paper URLs"""
    
    # Headers to mimic a real browser
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type(requests.RequestException),
        reraise=True
    )
    def _fetch_page(self, url: str) -> str:
        """
        Fetch page content with retry logic
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content as string
            
        Raises:
            ScraperError: If fetch fails
        """
        try:
            logger.info(f"Fetching: {url}")
            response = requests.get(url, headers=self.HEADERS, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            raise ScraperError(f"Failed to fetch page: {e}")
    
    def scrape_generic(self, url: str) -> Optional[str]:
        """
        Generic scraper for academic sites
        
        Args:
            url: Paper URL
            
        Returns:
            Abstract text or None if failed
        """
        try:
            html = self._fetch_page(url)
            soup = BeautifulSoup(html, 'html.parser')
            
            # Try common abstract selectors
            selectors = [
                ('class', ['abstract', 'Abstract', 'article-abstract', 'paper-abstract', 'abstract-content', 'abstractSection']),
                ('id', ['abstract', 'Abstract', 'abst']),
                ('data-testid', ['abstract'])
            ]
            
            for selector_type, values in selectors:
                for value in values:
                    if selector_type == 'data-testid':
                        elem = soup.find(['div', 'section'], attrs={selector_type: value})
                    elif selector_type == 'id':
                        elem = soup.find(['div', 'section'], id=value)
                    else:  # class
                        elem = soup.find(['div', 'section', 'p', 'blockquote'], class_=value)
                    
                    if elem:
                        content = elem.get_text(strip=True).replace('Abstract:', '').replace('Abstract', '').strip()
                        if len(content) > 100:
                            logger.info(f"✓ Scraped abstract ({len(content)} chars)")
                            return content
            
            # Fallback: Try meta tags
            for meta_attr in [('name', 'description'), ('property', 'og:description')]:
                meta = soup.find('meta', {meta_attr[0]: meta_attr[1]})
                if meta and meta.get('content'):
                    content = meta['content'].strip()
                    if len(content) > 100:
                        logger.info(f"✓ Scraped meta description ({len(content)} chars)")
                        return content
            
            logger.warning("No abstract found")
            return None
            
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            return None
    
    def scrape_paper(self, paper: Dict) -> Dict:
        """
        Scrape abstract for a paper
        
        Args:
            paper: Paper dict with 'link' key
            
        Returns:
            Paper dict with added 'abstract' field
        """
        url = paper.get('link', '')
        
        if not url:
            logger.warning("No URL provided")
            paper['abstract'] = None
            return paper
        
        logger.info(f"Scraping: {url}")
        paper['abstract'] = self.scrape_generic(url)
        
        return paper
    
    def scrape_papers(self, papers: list, max_workers: int = 5) -> list:
        """
        Scrape abstracts for multiple papers concurrently
        
        Args:
            papers: List of paper dicts
            max_workers: Maximum number of concurrent scraping threads (default: 5)
            
        Returns:
            List of papers with abstracts added
        """
        logger.info(f"Starting to scrape {len(papers)} papers (max_workers={max_workers})")
        
        scraped_papers = [None] * len(papers)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {executor.submit(self.scrape_paper, paper): i for i, paper in enumerate(papers)}
            
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    scraped_papers[index] = future.result()
                    logger.info(f"[{index + 1}/{len(papers)}] Completed")
                except Exception as e:
                    logger.error(f"[{index + 1}/{len(papers)}] Error: {e}")
                    scraped_papers[index] = papers[index]
                    scraped_papers[index]['abstract'] = None
        
        successful = sum(1 for p in scraped_papers if p.get('abstract'))
        logger.info(f"Scraping complete: {successful}/{len(papers)} successful")
        
        return scraped_papers


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scraper = PaperScraper()
    
    test_papers = [
        {'title': 'Attention Is All You Need', 'link': 'https://arxiv.org/abs/1706.03762'},
        {'title': 'Test Paper', 'link': 'https://pubmed.ncbi.nlm.nih.gov/12345678/'}
    ]
    
    results = scraper.scrape_papers(test_papers)
    
    for paper in results:
        print(f"\n{paper['title']}")
        print(f"Abstract: {paper.get('abstract', 'N/A')[:100]}...")
