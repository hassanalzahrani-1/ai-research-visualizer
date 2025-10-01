"""
End-to-End Testing Script for AI Research Paper Visualizer
Tests the complete workflow from search to image generation
"""

import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_health_check():
    """Test 1: Health Check"""
    print_section("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"✓ Status: {data['status']}")
        print(f"✓ Version: {data['version']}")
        print(f"✓ Services:")
        for service, status in data['services'].items():
            icon = "✓" if status == "ok" else "✗"
            print(f"  {icon} {service}: {status}")
        
        return data['status'] == 'healthy'
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

def test_search():
    """Test 2: Search Papers"""
    print_section("TEST 2: Search Papers")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/search",
            json={
                "query": "Attention Mechanism",
                "num_results": 3,
                "date_range": "year"
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        print(f"✓ Query: {data['query']}")
        print(f"✓ Found: {data['num_results']} papers\n")
        
        for i, paper in enumerate(data['papers'][:2], 1):
            print(f"{i}. {paper['title']}")
            print(f"   Authors: {paper['authors']}")
            print(f"   Year: {paper['year']}")
            print(f"   Citations: {paper['cited_by']}")
            print()
        
        return len(data['papers']) > 0
    except Exception as e:
        print(f"✗ Search failed: {e}")
        return False

def test_full_pipeline():
    """Test 3: Full Pipeline (Search + Scrape + Generate)"""
    print_section("TEST 3: Full Pipeline")
    
    try:
        print("Starting full pipeline (this may take 1-2 minutes)...")
        
        response = requests.post(
            f"{BASE_URL}/api/process",
            json={
                "query": "Transformer Neural Network",
                "num_papers": 2,
                "generate_images": True
            },
            timeout=300  # 5 minutes timeout
        )
        response.raise_for_status()
        data = response.json()
        
        print(f"\n✓ Query: {data['query']}")
        print(f"✓ Total papers: {data['total_papers']}")
        print(f"✓ Successful: {data['successful']}")
        print(f"✓ Success rate: {(data['successful']/data['total_papers']*100):.1f}%\n")
        
        for i, paper in enumerate(data['papers'], 1):
            print(f"{i}. {paper['title']}")
            print(f"   Link: {paper['link']}")
            print(f"   Abstract source: {paper['abstract_source']}")
            print(f"   Abstract length: {len(paper['abstract'])} chars")
            print(f"   Images generated: {len(paper['image_paths'])}")
            if paper['image_paths']:
                for img_path in paper['image_paths']:
                    print(f"   → {img_path}")
            print(f"   Processing: {'✓ Success' if paper['processing_success'] else '✗ Failed'}")
            print()
        
        return data['successful'] > 0
    except requests.exceptions.Timeout:
        print("✗ Pipeline timed out (this is normal for image generation)")
        print("  Check the server logs for progress")
        return False
    except Exception as e:
        print(f"✗ Pipeline failed: {e}")
        return False

def test_last_result():
    """Test 4: Get Last Result"""
    print_section("TEST 4: Get Last Result")
    
    try:
        response = requests.get(f"{BASE_URL}/api/last-result", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"✓ Last query: {data['query']}")
        print(f"✓ Papers processed: {data['total_papers']}")
        print(f"✓ Successful: {data['successful']}")
        
        return True
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print("✓ No previous results (expected if first run)")
            return True
        print(f"✗ Failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  AI RESEARCH PAPER VISUALIZER - E2E TESTS")
    print("="*60)
    print(f"\nTesting API at: {BASE_URL}")
    print("Make sure the server is running: python -m uvicorn backend.app:app --reload")
    
    # Wait for user confirmation
    input("\nPress Enter to start tests...")
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health_check()))
    results.append(("Search Papers", test_search()))
    results.append(("Full Pipeline", test_full_pipeline()))
    results.append(("Last Result", test_last_result()))
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        icon = "✓" if result else "✗"
        status = "PASSED" if result else "FAILED"
        print(f"{icon} {test_name}: {status}")
    
    print(f"\n{'='*60}")
    print(f"  Results: {passed}/{total} tests passed ({(passed/total*100):.1f}%)")
    print(f"{'='*60}\n")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)
