import React, { useState } from 'react';
import './priceTrack.css';

const PriceTrackerForm = () => {
  const [keyword, setKeyword] = useState('');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (keyword) {
      try {
        // Send the keyword to the backend
        const response = await fetch('http://localhost:5000/api/save-keyword', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ keyword }),
        });

        const result = await response.json();
        if (response.ok) {
          setMessage(result.message);
        } else {
          setMessage(result.error || 'Failed to save keyword.');
        }
        setKeyword('');
      } catch (error) {
        setMessage('Error occurred while saving the keyword.');
        console.error(error);
      }
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Enter Product Keyword"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          required
        />
        <button type="submit">Track Product</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default PriceTrackerForm;
