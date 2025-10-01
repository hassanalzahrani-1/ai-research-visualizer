import React from 'react';
import './ResultsDisplay.css';

function ResultsDisplay({ papers, onPaperSelect, selectedPaper }) {
  return (
    <div className="results-display">
      <div className="papers-grid">
        {papers.map((paper, index) => (
          <div
            key={index}
            className={`paper-card ${selectedPaper === paper ? 'selected' : ''}`}
            onClick={() => onPaperSelect(paper)}
          >
            <div className="paper-header">
              <h3 className="paper-title">{paper.title}</h3>
              <div className="paper-meta">
                {paper.year && <span className="meta-badge">📅 {paper.year}</span>}
                {paper.cited_by > 0 && (
                  <span className="meta-badge">📚 {paper.cited_by} citations</span>
                )}
              </div>
            </div>

            <div className="paper-body">
              <p className="paper-authors">
                <strong>Authors:</strong> {paper.authors}
              </p>
              <p className="paper-publication">
                <strong>Publication:</strong> {paper.publication_info}
              </p>
              <div className="paper-abstract">
                <strong>Abstract:</strong>
                <p>{paper.abstract}</p>
              </div>
              <div className="paper-source">
                <span className={`source-badge ${paper.abstract_source}`}>
                  {paper.abstract_source === 'scraped' ? '✓ Full Abstract' : '⚠ Snippet Only'}
                </span>
              </div>
            </div>

            <div className="paper-footer">
              <a
                href={paper.link}
                target="_blank"
                rel="noopener noreferrer"
                className="paper-link"
                onClick={(e) => e.stopPropagation()}
              >
                🔗 View Paper
              </a>
              {paper.image_paths.length > 0 && (
                <span className="image-count">
                  🎨 {paper.image_paths.length} image{paper.image_paths.length > 1 ? 's' : ''}
                </span>
              )}
              {!paper.processing_success && (
                <span className="error-badge">⚠ Processing Error</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ResultsDisplay;
