import React, { useState } from 'react';
import './App.css';
import SearchForm from './components/SearchForm';
import ResultsDisplay from './components/ResultsDisplay';
import ImageGallery from './components/ImageGallery';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  const [selectedPaper, setSelectedPaper] = useState(null);

  const handleSearch = async (searchParams) => {
    setLoading(true);
    setError(null);
    setResults(null);
    setSelectedPaper(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchParams.query,
          num_papers: searchParams.numResults,
          date_range: searchParams.dateRange,
          generate_images: searchParams.generateImages,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Search failed');
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err.message);
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePaperSelect = (paper) => {
    setSelectedPaper(paper);
  };

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-content">
          <h1>🔬 AI Research Paper Visualizer</h1>
          <p className="subtitle">Search academic papers and generate visual representations</p>
        </div>
      </header>

      <main className="App-main">
        <SearchForm onSearch={handleSearch} loading={loading} />

        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            <span>{error}</span>
          </div>
        )}

        {loading && (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>Searching papers and generating visualizations...</p>
            <p className="loading-subtext">This may take 30-60 seconds per paper</p>
          </div>
        )}

        {results && !loading && (
          <>
            <div className="results-summary">
              <h2>Results for "{results.query}"</h2>
              <p>
                Successfully processed <strong>{results.successful}</strong> of{' '}
                <strong>{results.total_papers}</strong> papers
              </p>
            </div>

            <ResultsDisplay
              papers={results.papers}
              onPaperSelect={handlePaperSelect}
              selectedPaper={selectedPaper}
            />

            {selectedPaper && selectedPaper.image_paths.length > 0 && (
              <ImageGallery images={selectedPaper.image_paths} title={selectedPaper.title} />
            )}
          </>
        )}
      </main>

      <footer className="App-footer">
        <p>
          Powered by <a href="https://serper.dev" target="_blank" rel="noopener noreferrer">Serper API</a> and{' '}
          <a href="https://scenario.com" target="_blank" rel="noopener noreferrer">Scenario API</a>
        </p>
      </footer>
    </div>
  );
}

export default App;
