import React, { useState } from 'react';
import './ImageGallery.css';

function ImageGallery({ images, title }) {
  const [selectedImage, setSelectedImage] = useState(null);

  const handleImageClick = (image) => {
    setSelectedImage(image);
  };

  const handleCloseModal = () => {
    setSelectedImage(null);
  };

  const getImageUrl = (imagePath) => {
    // Convert local path to API URL
    const filename = imagePath.split(/[/\\]/).pop();
    return `http://localhost:8000/images/${filename}`;
  };

  return (
    <div className="image-gallery">
      <h3 className="gallery-title">🎨 Generated Visualizations</h3>
      <p className="gallery-subtitle">{title}</p>
      
      <div className="gallery-grid">
        {images.map((image, index) => (
          <div key={index} className="gallery-item" onClick={() => handleImageClick(image)}>
            <img
              src={getImageUrl(image)}
              alt={`Visualization ${index + 1}`}
              className="gallery-image"
            />
            <div className="gallery-overlay">
              <span className="zoom-icon">🔍</span>
            </div>
          </div>
        ))}
      </div>

      {selectedImage && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={handleCloseModal}>
              ✕
            </button>
            <img
              src={getImageUrl(selectedImage)}
              alt="Full size visualization"
              className="modal-image"
            />
            <div className="modal-actions">
              <a
                href={getImageUrl(selectedImage)}
                download
                className="download-button"
                onClick={(e) => e.stopPropagation()}
              >
                💾 Download
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ImageGallery;
