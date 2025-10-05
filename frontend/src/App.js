import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import Aurora from './components/Aurora';
import MagicBento from './components/MagicBento';
import SplitText from './components/SplitText';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  
  // Form state
  const [query, setQuery] = useState('');
  const [numPapers, setNumPapers] = useState(5);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      // Step 1: Get papers fast (no images)
      const response = await fetch(`${API_BASE_URL}/api/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query.trim(),
          num_papers: numPapers
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Search failed');
      }

      const data = await response.json();
      setResults(data);
      setLoading(false);

      // Step 2: Load images progressively for each paper
      data.papers.forEach((paper, index) => {
        loadImageForPaper(paper, index);
      });

    } catch (err) {
      setError(err.message);
      console.error('Search error:', err);
      setLoading(false);
    }
  };

  const loadImageForPaper = async (paper, index) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/generate-image`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          paper: paper,  // Send entire paper object including abstract
        }),
      });

      if (response.ok) {
        const imageData = await response.json();
        if (imageData.success && imageData.image_urls.length > 0) {
          // Update the specific paper with its image
          setResults(prevResults => {
            if (!prevResults) return prevResults;
            const updatedPapers = [...prevResults.papers];
            updatedPapers[index] = {
              ...updatedPapers[index],
              image_urls: imageData.image_urls,
            };
            return {
              ...prevResults,
              papers: updatedPapers,
            };
          });
        }
      }
    } catch (err) {
      console.error(`Failed to load image for paper ${index}:`, err);
    }
  };

  return (
    <div className="App" style={{ backgroundColor: '#060010' }}>
      <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', zIndex: -1}}>
        <Aurora
          colorStops={["#3A29FF", "#FF94B4", "#FF3232"]}
          blend={1.5}
          amplitude={5}
          speed={0.5}
        />
      </div>
      
      <div className="container">
        <header className="header">
          <SplitText
            text="AI Research Visualizer"
            tag="h1"
            delay={0}
            duration={0.6}
            ease="power3.out"
            splitType="chars"
            from={{ opacity: 0, x: -50 }}
            to={{ opacity: 1, x: 0 }}
            threshold={0.2}
            rootMargin="0px"
            textAlign="center"
          />
          <SplitText
            text="Discover and visualize academic papers with AI-generated imagery"
            tag="p"
            className="subtitle"
            delay={0}
            duration={0.6}
            ease="power3.out"
            splitType="chars"
            from={{ opacity: 0, x: -50 }}
            to={{ opacity: 1, x: 0 }}
            threshold={0.2}
            rootMargin="0px"
            textAlign="center"
          />
        </header>

        <div className="search-section">
          <form onSubmit={handleSearch} className="search-form-inline">
            <div className="search-bar-container">
              <div className="dropdown-wrapper" ref={dropdownRef}>
                <button
                  type="button"
                  className="dropdown-button"
                  onClick={() => setDropdownOpen(!dropdownOpen)}
                  disabled={loading}
                >
                  {numPapers} Papers
                  <svg className="dropdown-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 10 6">
                    <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="m1 1 4 4 4-4"/>
                  </svg>
                </button>
                
                {dropdownOpen && (
                  <div className="dropdown-menu">
                    <ul>
                      <li>
                        <button type="button" onClick={() => { setNumPapers(3); setDropdownOpen(false); }}>
                          3 Papers
                        </button>
                      </li>
                      <li>
                        <button type="button" onClick={() => { setNumPapers(5); setDropdownOpen(false); }}>
                          5 Papers
                        </button>
                      </li>
                      <li>
                        <button type="button" onClick={() => { setNumPapers(10); setDropdownOpen(false); }}>
                          10 Papers
                        </button>
                      </li>
                      <li>
                        <button type="button" onClick={() => { setNumPapers(15); setDropdownOpen(false); }}>
                          15 Papers
                        </button>
                      </li>
                    </ul>
                  </div>
                )}
              </div>

              <div className="search-input-wrapper">
                <input
                  type="search"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search research papers..."
                  className="search-input-inline"
                  disabled={loading}
                  required
                />
                <button type="submit" className="search-btn-inline" disabled={loading || !query.trim()}>
                  <svg className="search-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 20">
                    <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z"/>
                  </svg>
                  <span className="sr-only">Search</span>
                </button>
              </div>
            </div>
          </form>
        </div>

        {error && (
          <div className="error-box">
            ⚠️ {error}
          </div>
        )}

        {loading && (
          <div className="loading-box">
            <div className="spinner"></div>
            <p>Searching for {numPapers} papers...</p>
          </div>
        )}

        {results && !loading && (
          <MagicBento 
            papers={results.papers}
            enableStars={true}
            enableSpotlight={true}
            enableBorderGlow={true}
            spotlightRadius={0}
            particleCount={8}
            glowColor="132, 0, 255"
          />
        )}
      </div>
    </div>
  );
}

export default App;
