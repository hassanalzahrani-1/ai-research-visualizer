# AI Research Paper Visualizer

An intelligent system that searches academic papers, extracts abstracts, and generates visual representations using AI. Combines Google Scholar search (via Serper API), web scraping, and AI image generation (via Scenario API) into a unified FastAPI backend.

## Features

- 🔍 **Google Scholar Search**: Search academic papers with date filtering
- 📄 **Smart Web Scraping**: Extract full abstracts from arXiv, IEEE, PubMed, ACM, Springer, and more
- 🎨 **AI Image Generation**: Create visual representations of research papers
- 🚀 **FastAPI Backend**: RESTful API with automatic documentation
- 🔄 **Full Pipeline**: End-to-end workflow from search to visualization
- 🛡️ **Robust Error Handling**: Retry logic and graceful fallbacks
- 📊 **Postman Collection**: Ready-to-use API testing collection

## Setup

### 1. Clone or Download

If you haven't already, navigate to your project directory.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Get API Credentials

You'll need API keys from two services:

#### Serper API (Google Scholar Search)
1. Sign up at [Serper.dev](https://serper.dev)
2. Get your API key from the dashboard
3. Free tier: 2,500 searches/month

#### Scenario API (Image Generation)
1. Sign up at [Scenario.com](https://scenario.com)
2. Get your API key and secret from the dashboard
3. Free tier available for testing

### 4. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   copy .env.example .env
   ```

2. Edit the `.env` file and add your credentials:
   ```env
   SERPER_API_KEY=your_serper_api_key_here
   SCENARIO_API_KEY=your_scenario_api_key_here
   SCENARIO_API_SECRET=your_scenario_api_secret_here
   ```

**Important**: The `.env` file is in `.gitignore` to protect your API keys.

## Usage

### Start the API Server

```bash
python -m uvicorn backend.app:app --reload
```

The API will be available at `http://localhost:8000`

- **API Documentation**: http://localhost:8000/api/docs
- **Alternative Docs**: http://localhost:8000/api/redoc

### API Endpoints

#### 1. Health Check
```bash
GET /api/health
```
Check API status and service availability.

#### 2. Search Papers
```bash
POST /api/search
Content-Type: application/json

{
  "query": "Artificial Intelligence",
  "num_results": 10,
  "date_range": "year"
}
```

#### 3. Scrape Abstracts
```bash
POST /api/scrape
Content-Type: application/json

[
  {
    "title": "Paper Title",
    "link": "https://arxiv.org/abs/...",
    "snippet": "...",
    "publication_info": "...",
    "cited_by": 100,
    "year": 2024,
    "authors": "..."
  }
]
```

#### 4. Generate Image
```bash
POST /api/generate-image
Content-Type: application/json

{
  "title": "Paper Title",
  "abstract": "Full abstract text...",
  "width": 1024,
  "height": 1024
}
```

#### 5. Full Pipeline (Recommended)
```bash
POST /api/process
Content-Type: application/json

{
  "query": "Machine Learning",
  "num_papers": 5,
  "date_range": "month",
  "generate_images": true
}
```

This endpoint runs the complete workflow:
1. Searches Google Scholar
2. Scrapes full abstracts
3. Generates visualization images
4. Returns processed papers with images

#### 6. Get Last Result
```bash
GET /api/last-result
```

### Using Postman

Import the provided `postman_collection.json` file into Postman:

1. Open Postman
2. Click "Import" → "Upload Files"
3. Select `postman_collection.json`
4. Set the `base_url` variable to `http://localhost:8000`
5. Start testing the API!

## Examples

### Example 1: Quick Search
```python
import requests

response = requests.post('http://localhost:8000/api/search', json={
    "query": "Deep Learning",
    "num_results": 5
})

papers = response.json()['papers']
for paper in papers:
    print(f"{paper['title']} - {paper['cited_by']} citations")
```

### Example 2: Full Pipeline
```python
import requests

response = requests.post('http://localhost:8000/api/process', json={
    "query": "Transformer Architecture",
    "num_papers": 3,
    "generate_images": True
})

result = response.json()
print(f"Processed {result['successful']}/{result['total_papers']} papers")

for paper in result['papers']:
    print(f"\nTitle: {paper['title']}")
    print(f"Abstract: {paper['abstract'][:200]}...")
    print(f"Images: {paper['image_paths']}")
```

## Output

Generated images are saved in the `output/` directory with timestamps:

```
output/
├── generated_image_20251001_153022_1.png
├── generated_image_20251001_153022_2.png
├── last_result.json
└── ...
```

## Security Features

- ✅ API keys stored in `.env` file (hidden from Git)
- ✅ `.env` file is in `.gitignore`
- ✅ Example template (`.env.example`) provided for setup
- ✅ No hardcoded credentials in source code

## Project Structure

```
ai-research-visualizer/
├── backend/
│   ├── __init__.py
│   ├── app.py              # FastAPI application
│   ├── models.py           # Pydantic models
│   ├── serper_client.py    # Google Scholar search client
│   ├── scenario_client.py  # Image generation client
│   └── scraper.py          # Web scraping module
├── output/                 # Generated images and results
├── .env.example           # Environment variables template
├── .env                   # Your API keys (gitignored)
├── .gitignore
├── requirements.txt       # Python dependencies
├── postman_collection.json # Postman API collection
└── README.md
```

## Troubleshooting

### "API credentials not found" Error
- Ensure `.env` file exists in the project root
- Verify all required API keys are set: `SERPER_API_KEY`, `SCENARIO_API_KEY`, `SCENARIO_API_SECRET`
- No extra spaces or quotes around values

### "ModuleNotFoundError" Error
- Activate virtual environment: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Unix)
- Install dependencies: `pip install -r requirements.txt`

### Scraping Failures
- Some sites block automated scraping
- The system automatically falls back to Serper snippets
- Check logs for specific error messages

### Image Generation Timeout
- Image generation can take 30-60 seconds per paper
- Check Scenario.com account credits
- Verify API key has generation permissions

### Rate Limiting
- Serper: 2,500 searches/month on free tier
- Scenario: Check your plan limits
- Implement delays between requests if needed

## Testing

### Manual Testing
1. Start the server: `python -m uvicorn backend.app:app --reload`
2. Open browser: http://localhost:8000/api/docs
3. Test each endpoint using the interactive Swagger UI

### Using Postman
1. Import `postman_collection.json`
2. Test individual endpoints
3. Run full pipeline test with `/api/process`

### End-to-End Test
```python
# test_e2e.py
import requests
import time

BASE_URL = "http://localhost:8000"

# 1. Health check
health = requests.get(f"{BASE_URL}/api/health")
print(f"Health: {health.json()['status']}")

# 2. Full pipeline
response = requests.post(f"{BASE_URL}/api/process", json={
    "query": "Attention Mechanism",
    "num_papers": 2,
    "generate_images": True
})

result = response.json()
print(f"\nProcessed: {result['successful']}/{result['total_papers']} papers")

for paper in result['papers']:
    print(f"\n✓ {paper['title']}")
    print(f"  Abstract source: {paper['abstract_source']}")
    print(f"  Images: {len(paper['image_paths'])}")
```

## Architecture

### Components
1. **Serper Client**: Google Scholar search with retry logic
2. **Web Scraper**: Multi-site abstract extraction with fallbacks
3. **Scenario Client**: AI image generation with polling
4. **FastAPI Backend**: RESTful API with validation
5. **Pydantic Models**: Request/response validation

### Workflow
```
Search Query → Serper API → Paper Results
     ↓
Paper URLs → Web Scraper → Full Abstracts
     ↓
Title + Abstract → Scenario API → Generated Images
     ↓
Complete Results → JSON Response + File Storage
```

## API Models

### Image Generation
- **Model**: `flux.1-dev` (high-quality text-to-image)
- **Resolution**: 512-2048px (configurable)
- **Scheduler**: EulerAncestralDiscreteScheduler
- **Steps**: 28 (default)
- **Guidance**: 3.5 (default)

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source. Please respect API providers' terms of service:
- [Serper.dev Terms](https://serper.dev/terms)
- [Scenario.com Terms](https://scenario.com/terms)

## Credits

Built with:
- FastAPI
- BeautifulSoup4
- Tenacity
- Pydantic
- Requests
