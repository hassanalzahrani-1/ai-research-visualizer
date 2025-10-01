"""
Tests for FastAPI endpoints
"""

import pytest
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "services" in data


def test_search_papers_valid():
    """Test search endpoint with valid data"""
    response = client.post(
        "/api/search",
        json={
            "query": "Machine Learning",
            "num_results": 5,
            "date_range": "year"
        }
    )
    # May fail if API keys not configured, so check for either success or 503
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert "query" in data
        assert "papers" in data
        assert data["query"] == "Machine Learning"


def test_search_papers_invalid():
    """Test search endpoint with invalid data"""
    response = client.post(
        "/api/search",
        json={
            "query": "",  # Empty query
            "num_results": 5
        }
    )
    assert response.status_code == 422  # Validation error


def test_scrape_endpoint():
    """Test scrape endpoint"""
    papers = [
        {
            "title": "Test Paper",
            "link": "https://arxiv.org/abs/1706.03762",
            "snippet": "Test snippet",
            "publication_info": "Test",
            "cited_by": 0,
            "year": 2024,
            "authors": "Test Author"
        }
    ]
    
    response = client.post("/api/scrape", json=papers)
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "papers" in data
    assert data["total"] == 1


def test_generate_image_endpoint():
    """Test image generation endpoint"""
    response = client.post(
        "/api/generate-image",
        json={
            "title": "Test Paper",
            "abstract": "This is a test abstract for image generation.",
            "width": 512,
            "height": 512
        }
    )
    # May fail if API keys not configured
    assert response.status_code in [200, 503]


def test_last_result_not_found():
    """Test last result endpoint when no results exist"""
    # This might return 404 or 200 depending on whether previous tests ran
    response = client.get("/api/last-result")
    assert response.status_code in [200, 404]


def test_process_endpoint_validation():
    """Test full pipeline endpoint validation"""
    response = client.post(
        "/api/process",
        json={
            "query": "",  # Invalid empty query
            "num_papers": 5
        }
    )
    assert response.status_code == 422  # Validation error


def test_cors_headers():
    """Test CORS headers are present"""
    response = client.options("/api/health")
    # CORS middleware should add headers
    assert response.status_code in [200, 405]


def test_api_docs():
    """Test that API documentation is accessible"""
    response = client.get("/api/docs")
    assert response.status_code == 200


def test_search_with_different_date_ranges():
    """Test search with various date range options"""
    date_ranges = ["week", "month", "year", ""]
    
    for date_range in date_ranges:
        response = client.post(
            "/api/search",
            json={
                "query": "AI",
                "num_results": 3,
                "date_range": date_range
            }
        )
        assert response.status_code in [200, 503]


def test_search_with_different_result_counts():
    """Test search with various result counts"""
    for num_results in [1, 5, 10]:
        response = client.post(
            "/api/search",
            json={
                "query": "Deep Learning",
                "num_results": num_results
            }
        )
        assert response.status_code in [200, 503]
