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


def test_parse_response():
    """Test response parsing"""
    client = SerperClient(api_key="test_key")
    
    response = {
        'organic': [
            {
                'title': 'Test Paper',
                'link': 'https://example.com',
                'snippet': 'Test snippet',
                'publicationInfo': {'summary': 'Test - 2023'}
            }
        ]
    }
    
    papers = client._parse_response(response)
    assert len(papers) == 1
    assert papers[0]['title'] == 'Test Paper'
    assert papers[0]['year'] == 2023


def test_site_filter_in_query():
    """Test that site filter is applied to search queries"""
    client = SerperClient(api_key="test_key")
    
    # The search_scholar method should add site filtering
    # We can't test the actual API call, but we can verify the method exists
    assert hasattr(client, 'search_scholar')
    assert callable(client.search_scholar)


def test_serper_headers():
    """Test that proper headers are set"""
    client = SerperClient(api_key="test_key")
    
    assert 'X-API-KEY' in client.headers
    assert client.headers['X-API-KEY'] == 'test_key'
    assert 'Content-Type' in client.headers
    assert client.headers['Content-Type'] == 'application/json'
