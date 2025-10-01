import React, { useState } from 'react';
import './SearchForm.css';

function SearchForm({ onSearch, loading }) {
  const [query, setQuery] = useState('');
  const [numResults, setNumResults] = useState(5);
  const [dateRange, setDateRange] = useState('year');
  const [generateImages, setGenerateImages] = useState(true);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch({
        query: query.trim(),
        numResults,
        dateRange,
        generateImages,
      });
    }
  };

  return (
    <div className="search-form-container">
      <form onSubmit={handleSubmit} className="search-form">
        <div className="form-group">
          <label htmlFor="query">
            <span className="label-icon">🔍</span>
            Search Query
          </label>
          <input
            type="text"
            id="query"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., Machine Learning, Neural Networks..."
            disabled={loading}
            required
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="numResults">
              <span className="label-icon">📊</span>
              Number of Papers
            </label>
            <select
              id="numResults"
              value={numResults}
              onChange={(e) => setNumResults(parseInt(e.target.value))}
              disabled={loading}
            >
              <option value="3">3 papers</option>
              <option value="5">5 papers</option>
              <option value="10">10 papers</option>
              <option value="15">15 papers</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="dateRange">
              <span className="label-icon">📅</span>
              Date Range
            </label>
            <select
              id="dateRange"
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              disabled={loading}
            >
              <option value="">All time</option>
              <option value="week">Past week</option>
              <option value="month">Past month</option>
              <option value="year">Past year</option>
            </select>
          </div>
        </div>

        <div className="form-group checkbox-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={generateImages}
              onChange={(e) => setGenerateImages(e.target.checked)}
              disabled={loading}
            />
            <span>🎨 Generate AI visualizations (takes longer)</span>
          </label>
        </div>

        <button type="submit" className="search-button" disabled={loading || !query.trim()}>
          {loading ? (
            <>
              <span className="button-spinner"></span>
              Searching...
            </>
          ) : (
            <>
              <span>🚀</span>
              Search Papers
            </>
          )}
        </button>
      </form>
    </div>
  );
}

export default SearchForm;
