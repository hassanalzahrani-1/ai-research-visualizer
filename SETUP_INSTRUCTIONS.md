# Setup Instructions

## Quick Start Guide

### Prerequisites
- Python 3.8+
- Node.js 14+ (for frontend)
- Git

### 1. Clone Repository
```bash
git clone <repository-url>
cd ai-research-visualizer
```

### 2. Backend Setup

#### Create Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# Unix/MacOS:
source .venv/bin/activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Configure Environment Variables
```bash
# Copy example file
copy .env.example .env  # Windows
# or
cp .env.example .env    # Unix/MacOS

# Edit .env and add your API keys:
# SERPER_API_KEY=your_key_here
# SCENARIO_API_KEY=your_key_here
# SCENARIO_API_SECRET=your_secret_here
```

#### Start Backend Server
```bash
python -m uvicorn backend.app:app --reload
```

Server will be available at: http://localhost:8000
- API Docs: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### 3. Frontend Setup (Optional)

```bash
cd frontend
npm install
npm start
```

Frontend will be available at: http://localhost:3000

### 4. Testing

#### Run E2E Tests
```bash
# Make sure backend is running first
python test_e2e.py
```

#### Use Postman
1. Import `postman_collection.json`
2. Set `base_url` variable to `http://localhost:8000`
3. Run requests

## Important Notes

### ⚠️ What NOT to Commit

The following are automatically ignored by `.gitignore`:

- ✅ `.venv/` - Virtual environment (recreate with `python -m venv .venv`)
- ✅ `.env` - Your API keys (use `.env.example` as template)
- ✅ `node_modules/` - Node dependencies (reinstall with `npm install`)
- ✅ `__pycache__/` - Python cache
- ✅ `output/` - Generated images
- ✅ `*.log` - Log files

### ✅ What to Commit

- Source code (`backend/`, `frontend/src/`)
- Configuration templates (`.env.example`)
- Documentation (`README.md`, `*.md`)
- Dependencies (`requirements.txt`, `package.json`)
- Tests (`test_*.py`)

## Troubleshooting

### Virtual Environment Issues

**Problem**: `.venv/` was accidentally committed
```bash
# Remove from git (keeps local files)
git rm -r --cached .venv/
git commit -m "chore: Remove .venv from tracking"
```

**Problem**: Virtual environment not activating
```bash
# Delete and recreate
rm -rf .venv
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### API Key Issues

**Problem**: "API credentials not found"
```bash
# Check .env file exists
ls .env

# Verify format (no quotes, no spaces)
SERPER_API_KEY=abc123xyz
SCENARIO_API_KEY=def456uvw
```

### Port Already in Use

**Problem**: Port 8000 already in use
```bash
# Use different port
uvicorn backend.app:app --port 8001

# Or kill existing process
# Windows:
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Unix/MacOS:
lsof -ti:8000 | xargs kill -9
```

## Development Workflow

### Starting Development Session

```bash
# 1. Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Unix/MacOS

# 2. Pull latest changes
git pull origin master

# 3. Start backend
python -m uvicorn backend.app:app --reload

# 4. (Optional) Start frontend in new terminal
cd frontend
npm start
```

### Creating New Feature

```bash
# 1. Create feature branch
git checkout -b feature/your-feature

# 2. Make changes
# ... code ...

# 3. Test changes
python test_e2e.py

# 4. Commit
git add .
git commit -m "feat: Description"

# 5. Merge to master
git checkout master
git merge feature/your-feature
```

## API Keys

### Get Serper API Key
1. Go to https://serper.dev
2. Sign up for free account
3. Copy API key from dashboard
4. Add to `.env`: `SERPER_API_KEY=your_key`

### Get Scenario API Keys
1. Go to https://scenario.com
2. Sign up for account
3. Navigate to API settings
4. Copy API Key and Secret
5. Add to `.env`:
   ```
   SCENARIO_API_KEY=your_key
   SCENARIO_API_SECRET=your_secret
   ```

## Project Structure

```
ai-research-visualizer/
├── backend/              # Python FastAPI backend
│   ├── app.py           # Main API application
│   ├── models.py        # Pydantic models
│   ├── serper_client.py # Google Scholar search
│   ├── scenario_client.py # Image generation
│   └── scraper.py       # Web scraping
├── frontend/            # React frontend (optional)
├── output/              # Generated images (gitignored)
├── .venv/              # Virtual environment (gitignored)
├── .env                # API keys (gitignored)
├── .env.example        # Template for .env
├── requirements.txt    # Python dependencies
├── postman_collection.json # API testing
├── test_e2e.py        # End-to-end tests
└── README.md          # Main documentation
```

## Next Steps

1. ✅ Setup complete? Test with: `python test_e2e.py`
2. 📚 Read full documentation: `README.md`
3. 🔧 Development guide: `DEVELOPMENT_GUIDE.md`
4. 📊 Project overview: `PROJECT_SUMMARY.md`
5. 🚀 Start building!

## Support

- **API Documentation**: http://localhost:8000/api/docs
- **Issues**: Check `README.md` troubleshooting section
- **Questions**: See `DEVELOPMENT_GUIDE.md`

---

**Last Updated**: October 1, 2025
