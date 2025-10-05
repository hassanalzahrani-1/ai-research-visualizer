# AI Research Visualizer

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/hassanalzahrani-1/ai-research-visualizer)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

An intelligent system that searches academic papers, scrapes full abstracts, and generates AI-powered visual representations. Built with React, FastAPI, Serper API (Google Scholar search), web scraping, and Scenario API (AI image generation).

## ✨ Features

- 🔍 **Smart Search**: Google Scholar search with 2025+ date filtering and site restrictions
- 📄 **Web Scraping**: Extracts full abstracts from arXiv, PubMed, and ResearchGate
- 🎨 **AI Image Generation**: Creates visual representations using Scenario's Flux.1-dev model
- 🖼️ **Modern UI**: Aurora animated background with MagicBento grid layout and animated text
- 🎭 **Interactive Cards**: Particle effects, spotlight glow, and 3D tilt on hover
- 🚀 **FastAPI Backend**: RESTful API with automatic Swagger documentation
- 🔄 **Progressive Loading**: Images generate asynchronously for fast initial response
- 🛡️ **Robust Error Handling**: Retry logic with exponential backoff on all API calls
- 🔒 **Query Isolation**: Prevents search query contamination in image generation
- 📊 **Postman Collection**: Pre-configured API testing collection (v1.0.0)

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

### Option 1: Use the Web Interface (Recommended)

#### Start the Backend
```bash
python -m uvicorn backend.app:app --reload
```

#### Start the Frontend
In a new terminal:
```bash
cd frontend
npm install  # First time only
npm start
```

The web app will open at `http://localhost:3000`

### Option 2: Use the API Directly

Start the API server:
```bash
python -m uvicorn backend.app:app --reload
```

The API will be available at `http://localhost:8000`

- **API Documentation**: http://localhost:8000/api/docs
- **Alternative Docs**: http://localhost:8000/api/redoc

### API Endpoints

#### 1. Process Papers (Main Endpoint)
```bash
POST /api/process
Content-Type: application/json

{
  "query": "artificial intelligence",
  "num_papers": 5
}
```

**Response:**
```json
{
  "query": "artificial intelligence",
  "papers": [
    {
      "title": "Paper Title",
      "link": "https://arxiv.org/abs/...",
      "snippet": "Short description...",
      "year": 2025,
      "abstract": "Full scraped abstract (1500+ chars)...",
      "image_urls": []  // Populated progressively by frontend
    }
  ]
}
```

**Workflow:**
1. Searches Google Scholar (2025+ papers from arXiv/PubMed/ResearchGate)
2. Scrapes full abstracts from paper URLs
3. Returns papers immediately (fast response)
4. Frontend progressively loads images via `/api/generate-image`

#### 2. Generate Image
```bash
POST /api/generate-image
Content-Type: application/json

{
  "paper": {
    "title": "Paper Title",
    "snippet": "...",
    "abstract": "Full abstract...",
    "year": 2025
  }
}
```

**Response:**
```json
{
  "image_urls": ["https://cdn.scenario.com/..."],
  "success": true
}
```

#### 3. Health Check
```bash
GET /api/health
```
Returns API status and service availability.

### Using Postman

Import the provided `postman_collection.json` file into Postman:

1. Open Postman
2. Click "Import" → "Upload Files"
3. Select `postman_collection.json`
4. Set the `base_url` variable to `http://localhost:8000`
5. Start testing the API!

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
├── frontend/
│   ├── public/             # Static assets
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── Aurora.js          # Animated background
│   │   │   ├── MagicBento.js      # Bento grid with effects
│   │   │   ├── PaperModal.js      # Paper details modal
│   │   │   ├── SplitText.js       # Animated text component
│   │   │   └── AnimatedContent.js # Animation wrapper
│   │   ├── App.js          # Main app component
│   │   └── index.js        # Entry point
│   ├── package.json        # Node dependencies
│   └── .env                # Frontend environment (gitignored)
├── tests/
│   ├── test_api.py         # API endpoint tests
│   ├── test_serper_client.py
│   └── test_scraper.py
├── output/                 # Generated images and results
├── .env.example           # Environment variables template
├── .env                   # Your API keys (gitignored)
├── .gitignore
├── requirements.txt       # Python dependencies
├── pytest.ini             # Pytest configuration
├── test_e2e.py            # End-to-end test script
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
- Site filter restricts to arXiv, PubMed, and ResearchGate (scrapable sources)
- If scraping fails, `abstract` field will be `null` (frontend uses snippet as fallback)
- Check `scraper_results.json` for detailed scraping logs

### Image Generation Timeout
- Image generation can take 30-60 seconds per paper
- Check Scenario.com account credits
- Verify API key has generation permissions

### Rate Limiting
- Serper: 2,500 searches/month on free tier
- Scenario: Check your plan limits
- Implement delays between requests if needed

## Testing

### Automated Tests

Run the test suite:
```bash
# Install test dependencies (if not already installed)
pip install -r requirements.txt

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_api.py
```

### End-to-End Test

Run the complete workflow test:
```bash
# Make sure the backend is running first
python -m uvicorn backend.app:app --reload

# In another terminal, run the E2E test
python test_e2e.py
```

This will test:
1. ✓ Health check
2. ✓ Search papers
3. ✓ Full pipeline (search + scrape + generate)
4. ✓ Last result retrieval

### Manual Testing

#### Using the Web Interface
1. Start backend and frontend (see Usage section)
2. Open http://localhost:3000
3. Enter a search query and click "Search Papers"
4. View results and generated images

#### Using Postman
1. Import `postman_collection.json`
2. Set `base_url` to `http://localhost:8000`
3. Test individual endpoints
4. Run full pipeline test with `/api/process`

#### Using Swagger UI
1. Start the server: `python -m uvicorn backend.app:app --reload`
2. Open browser: http://localhost:8000/api/docs
3. Test each endpoint using the interactive interface

## Architecture

### Components
1. **React Frontend**: Aurora background, MagicBento grid with particle effects, spotlight glow, 3D tilt, animated text
2. **Serper Client**: Google Scholar search with site filtering, retry logic, and query isolation
3. **Web Scraper**: Optimized abstract extraction from arXiv, PubMed, ResearchGate (46% smaller codebase)
4. **Scenario Client**: AI image generation with Flux.1-dev model and adaptive polling
5. **FastAPI Backend**: RESTful API with Pydantic validation and snippet filtering
6. **Error Handling**: Exponential backoff retry logic on all external API calls

### Workflow
```
1. User searches → Serper API (filtered: arXiv/PubMed/ResearchGate, 2025+)
2. Get paper URLs → Web Scraper extracts full abstracts
3. Return papers immediately (fast response)
4. Frontend progressively calls /api/generate-image for each paper
5. Scenario API generates images (30-60s each)
6. Images appear as they complete
```

### Key Features
- **Site Filtering**: `(site:arxiv.org OR site:pubmed.ncbi.nlm.nih.gov OR site:researchgate.net)`
- **Progressive Loading**: Papers load instantly, images generate asynchronously
- **Abstract Truncation**: Full abstracts stored, but truncated to 500 chars for image prompts (faster generation)
- **Modal View**: Click any card to see full abstract and large image
- **Animated UI**: GSAP-powered text animations, particle effects, and spotlight interactions

## Technical Details

### Image Generation
- **Model**: Scenario Flux.1-dev (high-quality text-to-image)
- **Resolution**: 1024x1024px
- **Prompt**: Paper JSON (title, abstract, year) - snippet excluded to prevent query contamination
- **Generation Time**: 30-60 seconds per image


### Web Scraping
- **Priority**: HTML class/ID selectors → Meta tags → Fallback to snippet
- **Retry Logic**: 2 attempts with exponential backoff
- **Success Rate**: ~100% for arXiv/PubMed, varies for ResearchGate

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

## Technologies

**Backend:**
- FastAPI - RESTful API framework
- BeautifulSoup4 - HTML parsing for web scraping
- Tenacity - Retry logic with exponential backoff
- Pydantic - Data validation
- Requests - HTTP client

**Frontend:**
- React - UI framework
- GSAP - Advanced animations (SplitText, ScrollTrigger)
- CSS3 - Modern styling with glassmorphism and gradient effects
- Lucide React - Icon library

**APIs:**
- Serper API - Google Scholar search
- Scenario API - AI image generation (Flux.1-dev model)