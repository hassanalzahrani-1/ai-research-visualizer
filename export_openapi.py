"""
Export FastAPI OpenAPI schema for Postman collection generation
"""

import json
from backend.app import app

if __name__ == "__main__":
    # Get OpenAPI schema
    openapi_schema = app.openapi()
    
    # Save to file
    with open('openapi.json', 'w') as f:
        json.dump(openapi_schema, f, indent=2)
    
    print("✅ OpenAPI schema exported to openapi.json")
    print(f"   Title: {openapi_schema['info']['title']}")
    print(f"   Version: {openapi_schema['info']['version']}")
    print(f"   Endpoints: {len(openapi_schema['paths'])}")
