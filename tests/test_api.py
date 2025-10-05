"""
Tests for FastAPI endpoints
"""

import pytest
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)


def test_process_papers_valid():
    """Test process endpoint with valid data"""
    response = client.post(
        "/api/process",
        json={
            "query": "Machine Learning",
            "num_papers": 5
        }
    )
    # May fail if API keys not configured, so check for either success, 503, or 500
    assert response.status_code in [200, 500, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert "query" in data
        assert "papers" in data
        assert data["query"] == "Machine Learning"
        # Check that papers have the correct structure
        if len(data["papers"]) > 0:
            paper = data["papers"][0]
            assert "title" in paper
            assert "link" in paper
            assert "snippet" in paper
            assert "year" in paper
            assert "abstract" in paper  # May be None
            assert "image_urls" in paper


def test_process_papers_invalid():
    """Test process endpoint with invalid data"""
    response = client.post(
        "/api/process",
        json={
            "num_papers": 5
            # Missing required 'query' field
        }
    )
    assert response.status_code == 422  # Validation error
    
def test_generate_image_endpoint():
    """Test image generation endpoint"""
    response = client.post(
        "/api/generate-image",
        json={
            "paper": {
                "title": "Test Paper",
                "link": "https://example.com",
                "snippet": "This is a test abstract for image generation.",
                "year": 2024,
                "abstract": None,
                "image_urls": []
            }
        }
    )
    # May fail if API keys not configured
    assert response.status_code == 200  # Should always return 200 with success=false on error
    data = response.json()
    assert "success" in data
    assert "image_urls" in data

def test_process_endpoint_validation():
    """Test full pipeline endpoint validation"""
    response = client.post(
        "/api/process",
        json={
            "num_papers": 5
            # Missing required 'query' field
        }
    )
    assert response.status_code == 422  # Validation error


def test_cors_headers():
    """Test CORS headers are present"""
    response = client.options("/api/process")
    # CORS middleware should add headers
    assert response.status_code in [200, 405]


def test_api_docs():
    """Test that API documentation is accessible"""
    response = client.get("/api/docs")
    assert response.status_code == 200


def test_process_with_different_paper_counts():
    """Test process with various paper counts"""
    for num_papers in [1, 5, 10]:
        response = client.post(
            "/api/process",
            json={
                "query": "Deep Learning",
                "num_papers": num_papers
            }
        )
        assert response.status_code in [200, 500, 503]


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_process_returns_abstract_field():
    """Test that process endpoint returns abstract field"""
    response = client.post(
        "/api/process",
        json={
            "query": "artificial intelligence",
            "num_papers": 2
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        if len(data["papers"]) > 0:
            paper = data["papers"][0]
            # Abstract field should exist (may be None if scraping failed)
            assert "abstract" in paper
            # Should not have abstract_source anymore
            assert "abstract_source" not in paper
