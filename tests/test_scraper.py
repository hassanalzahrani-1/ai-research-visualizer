"""
Tests for Web Scraper
"""

import pytest
from backend.scraper import PaperScraper


def test_scraper_initialization():
    """Test scraper initialization"""
    scraper = PaperScraper()
    assert 'User-Agent' in scraper.HEADERS


def test_scrape_paper_no_url():
    """Test scraping with no URL"""
    scraper = PaperScraper()
    
    paper = {
        'title': 'Test Paper',
        'link': '',
        'snippet': 'Test snippet'
    }
    
    result = scraper.scrape_paper(paper)
    assert result['abstract'] is None


def test_scrape_paper_invalid_url():
    """Test scraping with invalid URL"""
    scraper = PaperScraper()
    
    paper = {
        'title': 'Test Paper',
        'link': 'https://invalid-url-that-does-not-exist.com',
        'snippet': 'Test snippet'
    }
    
    result = scraper.scrape_paper(paper)
    # Should return None for abstract (no fallback)
    assert result['abstract'] is None


def test_scrape_papers_batch():
    """Test batch scraping"""
    scraper = PaperScraper()
    
    papers = [
        {
            'title': 'Paper 1',
            'link': 'https://invalid-url-1.com',
            'snippet': 'Snippet 1'
        },
        {
            'title': 'Paper 2',
            'link': 'https://invalid-url-2.com',
            'snippet': 'Snippet 2'
        }
    ]
    
    result = scraper.scrape_papers(papers)
    
    assert len(result) == 2
    assert all('abstract' in paper for paper in result)
    # All should be None since URLs are invalid
    assert all(paper['abstract'] is None for paper in result)


def test_scrape_papers_empty_list():
    """Test batch scraping with empty list"""
    scraper = PaperScraper()
    result = scraper.scrape_papers([])
    assert result == []


def test_scrape_generic_method():
    """Test generic scraper method exists"""
    scraper = PaperScraper()
    # Should have scrape_generic method
    assert hasattr(scraper, 'scrape_generic')
    assert callable(scraper.scrape_generic)


def test_scraper_saves_results_to_file():
    """Test that scraper saves results to JSON file"""
    import os
    scraper = PaperScraper()
    
    papers = [
        {
            'title': 'Test Paper',
            'link': 'https://example.com',
            'snippet': 'Test snippet'
        }
    ]
    
    try:
        # Run scraper with save_results=True
        scraper.scrape_papers(papers, save_results=True)
        
        # Check if file was created
        assert os.path.exists('scraper_results.json')
    finally:
        # Always clean up, even if test fails
        if os.path.exists('scraper_results.json'):
            os.remove('scraper_results.json')


def test_scraper_handles_arxiv_urls():
    """Test that scraper recognizes arXiv URLs"""
    scraper = PaperScraper()
    
    paper = {
        'title': 'Test arXiv Paper',
        'link': 'https://arxiv.org/abs/1234.5678',
        'snippet': 'Test snippet'
    }
    
    result = scraper.scrape_paper(paper)
    # Should attempt to scrape (will fail for fake ID, but that's ok)
    assert 'abstract' in result
