# Development Guide

## Branch Strategy

### Current Branch Structure

```
master (main branch)
├── feature/serper-api ✅ (merged)
├── feature/scenario-api ✅ (merged)
├── feature/web-scraper ✅ (merged)
├── feature/backend-api ✅ (merged)
└── feature/frontend (recommended for React app)
```

### Frontend Development

The frontend should be developed on a separate branch:

```bash
# Create frontend branch from master
git checkout master
git checkout -b feature/frontend

# Frontend will be in the frontend/ directory
cd frontend
npm start
```

**Why separate branch?**
- ✅ Keep frontend and backend development independent
- ✅ Easy to review frontend changes separately
- ✅ Can deploy backend without frontend
- ✅ Different team members can work on each
- ✅ Cleaner git history

### Recommended Workflow

#### Option 1: Monorepo (Current Setup)
```
ai-research-visualizer/
├── backend/          # Python FastAPI
├── frontend/         # React app
├── requirements.txt  # Python deps
└── README.md
```

**Pros:**
- Single repository
- Easy to keep in sync
- Shared documentation

**Cons:**
- Mixed dependencies (Python + Node.js)
- Larger repository size

#### Option 2: Separate Repositories
```
ai-research-visualizer-backend/  # Python API
ai-research-visualizer-frontend/ # React app
```

**Pros:**
- Clean separation
- Independent deployment
- Smaller repos

**Cons:**
- Need to manage two repos
- API versioning required

### Recommended: Monorepo with Feature Branches

```bash
# Backend work (already done)
git checkout master

# Frontend work (next step)
git checkout -b feature/frontend
# Develop React app in frontend/
git add frontend/
git commit -m "feat: Add React frontend"

# When ready, merge to master
git checkout master
git merge feature/frontend
```

## Git Workflow

### Creating a New Feature

```bash
# 1. Start from master
git checkout master
git pull origin master

# 2. Create feature branch
git checkout -b feature/your-feature-name

# 3. Make changes
# ... code ...

# 4. Commit changes
git add .
git commit -m "feat: Description of feature"

# 5. Push to remote
git push origin feature/your-feature-name

# 6. Create Pull Request (if using GitHub/GitLab)
# Or merge locally:
git checkout master
git merge feature/your-feature-name
```

### Branch Naming Convention

- `feature/` - New features (e.g., `feature/frontend`, `feature/auth`)
- `fix/` - Bug fixes (e.g., `fix/scraper-timeout`)
- `docs/` - Documentation (e.g., `docs/api-guide`)
- `refactor/` - Code refactoring (e.g., `refactor/client-structure`)
- `test/` - Testing (e.g., `test/integration-tests`)

## Frontend Development

### Setup Frontend Branch

```bash
# Create and switch to frontend branch
git checkout -b feature/frontend

# The frontend/ directory already exists from create-react-app
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### Frontend Structure (Recommended)

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── SearchForm.jsx
│   │   ├── PaperCard.jsx
│   │   ├── ImageGallery.jsx
│   │   └── LoadingSpinner.jsx
│   ├── services/
│   │   └── api.js          # API client
│   ├── hooks/
│   │   └── usePapers.js    # Custom hooks
│   ├── App.jsx
│   ├── App.css
│   └── index.js
├── .env.example
├── package.json
└── README.md
```

### Frontend API Integration

Create `frontend/src/services/api.js`:

```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const searchPapers = async (query, numResults = 10, dateRange = null) => {
  const response = await fetch(`${API_BASE_URL}/api/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, num_results: numResults, date_range: dateRange })
  });
  return response.json();
};

export const processPapers = async (query, numPapers = 5, generateImages = true) => {
  const response = await fetch(`${API_BASE_URL}/api/process`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      query, 
      num_papers: numPapers, 
      generate_images: generateImages 
    })
  });
  return response.json();
};
```

### Frontend Environment Variables

Create `frontend/.env.example`:

```env
REACT_APP_API_URL=http://localhost:8000
```

## .gitignore Best Practices

### What to Ignore

✅ **Always ignore:**
- `.env` files (API keys)
- `node_modules/` (frontend dependencies)
- `.venv/` or `venv/` (Python virtual environment)
- `__pycache__/` (Python cache)
- `output/` (generated images)
- IDE files (`.vscode/`, `.idea/`)
- OS files (`.DS_Store`, `Thumbs.db`)

✅ **Consider ignoring:**
- `package-lock.json` or `yarn.lock` (if team uses different package managers)
- Build directories (`frontend/build/`, `dist/`)
- Log files (`*.log`)

❌ **Never ignore:**
- Source code
- Configuration templates (`.env.example`)
- Documentation
- Tests
- `requirements.txt` or `package.json`

## Deployment Strategy

### Backend Deployment

```bash
# Option 1: Docker
docker build -t ai-research-api .
docker run -p 8000:8000 ai-research-api

# Option 2: Direct deployment
pip install -r requirements.txt
uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

### Frontend Deployment

```bash
# Build for production
cd frontend
npm run build

# Deploy build/ directory to:
# - Vercel
# - Netlify
# - AWS S3 + CloudFront
# - GitHub Pages
```

### Full Stack Deployment

**Option 1: Separate Deployments**
- Backend → Heroku/Railway/Render
- Frontend → Vercel/Netlify

**Option 2: Single Server**
- FastAPI serves React build
- Update `backend/app.py` to serve static files

## Next Steps

### Immediate Actions

1. **Commit .gitignore updates:**
   ```bash
   git add .gitignore
   git commit -m "chore: Update .gitignore for frontend and additional files"
   ```

2. **Clean up frontend directory (optional):**
   ```bash
   # If you want to start fresh with frontend
   rm -rf frontend/
   
   # Or keep it and create feature branch
   git checkout -b feature/frontend
   ```

3. **Decide on frontend approach:**
   - Keep React app in monorepo (recommended)
   - Or move to separate repository

### Future Development

- [ ] Implement React frontend on `feature/frontend` branch
- [ ] Add authentication system
- [ ] Implement caching layer
- [ ] Add database for storing results
- [ ] Create Docker configuration
- [ ] Set up CI/CD pipeline
- [ ] Add more tests (unit, integration)

## Questions?

- **Should frontend be in same repo?** → Yes, monorepo is fine for this project
- **Should frontend be on separate branch?** → Yes, use `feature/frontend`
- **When to merge frontend?** → When it's functional and tested
- **How to handle package-lock.json?** → Already in .gitignore, team can decide

## Summary

✅ **Current Status:**
- Backend complete on `master`
- Frontend directory exists but not developed
- .gitignore updated

✅ **Recommended Next Steps:**
1. Commit .gitignore updates
2. Create `feature/frontend` branch
3. Develop React app
4. Merge when ready

✅ **Branch Strategy:**
- `master` - Production-ready code
- `feature/*` - New features
- Keep frontend on `feature/frontend` until ready
