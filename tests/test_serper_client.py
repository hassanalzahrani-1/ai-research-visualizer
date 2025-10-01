"""
Tests for Serper API Client
"""

import pytest
import os
from backend.serper_client import SerperClient, SerperAPIError


def test_serper_client_initialization():
    """Test SerperClient initialization"""
    # Should raise error if no API key
    original_key = os.environ.get('SERPER_API_KEY')
    if 'SERPER_API_KEY' in os.environ:
        del os.environ['SERPER_API_KEY']
    
    with pytest.raises(ValueError):
        SerperClient()
    
    # Restore original key
    if original_key:
        os.environ['SERPER_API_KEY'] = original_key


def test_serper_client_with_api_key():
    """Test SerperClient with API key"""
    try:
        client = SerperClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert 'X-API-KEY' in client.headers
    except Exception as e:
        pytest.fail(f"Client initialization failed: {e}")


def test_extract_citations():
    """Test citation extraction"""
    client = SerperClient(api_key="test_key")
    
    result = {
        'inlineLinks': [
            {'title': 'Cited by 123'}
        ]
    }
    
    citations = client._extract_citations(result)
    assert citations == 123


def test_extract_citations_no_data():
    """Test citation extraction with no data"""
    client = SerperClient(api_key="test_key")
    
    result = {'inlineLinks': []}
    citations = client._extract_citations(result)
    assert citations == 0


def test_extract_year():
    """Test year extraction"""
    client = SerperClient(api_key="test_key")
    
    result = {
        'publicationInfo': {
            'summary': 'Published in 2023'
        }
    }
    
    year = client._extract_year(result)
    assert year == 2023


def test_extract_year_no_data():
    """Test year extraction with no data"""
    client = SerperClient(api_key="test_key")
    
    result = {'publicationInfo': {'summary': ''}}
    year = client._extract_year(result)
    assert year is None


def test_extract_authors():
    """Test author extraction"""
    client = SerperClient(api_key="test_key")
    
    result = {
        'publicationInfo': {
            'summary': 'John Doe, Jane Smith - 2023'
        }
    }
    
    authors = client._extract_authors(result)
    assert 'John Doe' in authors


def test_parse_response():
    """Test response parsing"""
    client = SerperClient(api_key="test_key")
    
    response = {
        'organic': [
            {
                'title': 'Test Paper',
                'link': 'https://example.com',
                'snippet': 'Test snippet',
                'publicationInfo': {'summary': 'Test - 2023'},
                'inlineLinks': [{'title': 'Cited by 10'}]
            }
        ]
    }
    
    papers = client._parse_response(response)
    assert len(papers) == 1
    assert papers[0]['title'] == 'Test Paper'
    assert papers[0]['cited_by'] == 10
    assert papers[0]['year'] == 2023
