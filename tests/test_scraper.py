"""
Tests for Web Scraper
"""

import pytest
from backend.scraper import PaperScraper


def test_scraper_initialization():
    """Test scraper initialization"""
    scraper = PaperScraper()
    assert scraper.timeout == 10
    assert 'User-Agent' in scraper.headers


def test_scraper_custom_timeout():
    """Test scraper with custom timeout"""
    scraper = PaperScraper(timeout=20)
    assert scraper.timeout == 20


def test_scrape_abstract_with_fallback():
    """Test scraping with fallback to snippet"""
    scraper = PaperScraper()
    
    # Invalid URL should fall back to snippet
    result = scraper.scrape_abstract(
        url="https://invalid-url-that-does-not-exist.com",
        fallback_snippet="This is a fallback snippet"
    )
    
    assert result['abstract'] == "This is a fallback snippet"
    assert result['source'] == 'snippet'
    assert result['success'] is False


def test_batch_scrape():
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
    
    result = scraper.batch_scrape(papers)
    
    assert len(result) == 2
    assert all('abstract' in paper for paper in result)
    assert all('abstract_source' in paper for paper in result)
    assert all('scrape_success' in paper for paper in result)


def test_scrape_arxiv_url_structure():
    """Test that arXiv URLs are recognized"""
    scraper = PaperScraper()
    
    # This will likely fail to scrape but should try the arXiv scraper
    result = scraper.scrape_abstract(
        url="https://arxiv.org/abs/9999.99999",  # Invalid paper ID
        fallback_snippet="Fallback"
    )
    
    # Should fall back to snippet since paper doesn't exist
    assert result['source'] == 'snippet'


def test_batch_scrape_empty_list():
    """Test batch scraping with empty list"""
    scraper = PaperScraper()
    result = scraper.batch_scrape([])
    assert result == []


def test_scrape_abstract_short_text():
    """Test that short abstracts trigger fallback"""
    scraper = PaperScraper()
    
    # Even if we get content, if it's too short, should use fallback
    result = scraper.scrape_abstract(
        url="https://example.com",
        fallback_snippet="This is a longer fallback snippet that should be used"
    )
    
    # Should use fallback
    assert result['source'] == 'snippet'
