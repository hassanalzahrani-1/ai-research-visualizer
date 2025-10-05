import React, { useEffect } from 'react';
import './PaperModal.css';

const PaperModal = ({ paper, onClose }) => {
  // Close on Escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [onClose]);

  // Prevent body scroll when modal is open
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, []);

  if (!paper) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>

        <div className="modal-body">
          {/* Image Section */}
          <div className="modal-image-section">
            {paper.image_urls && paper.image_urls.length > 0 ? (
              <img 
                src={paper.image_urls[0]} 
                alt={paper.title} 
                className="modal-image"
              />
            ) : (
              <div className="modal-image-placeholder">
                <div className="loading-spinner"></div>
                <p>Generating image...</p>
              </div>
            )}
          </div>

          {/* Content Section */}
          <div className="modal-text-section">
            <div className="modal-header">
              <span className="modal-year">{paper.year || 'Research Paper'}</span>
              <h2 className="modal-title">{paper.title}</h2>
            </div>

            <div className="modal-abstract">
              <h3>Abstract</h3>
              <p>{paper.abstract || paper.snippet}</p>
            </div>

            <div className="modal-footer">
              <a 
                href={paper.link} 
                target="_blank" 
                rel="noopener noreferrer"
                className="modal-link-button"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                  <polyline points="15 3 21 3 21 9"></polyline>
                  <line x1="10" y1="14" x2="21" y2="3"></line>
                </svg>
                View Full Paper
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PaperModal;
