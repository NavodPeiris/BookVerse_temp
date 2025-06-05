import React, { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';

const Success = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const token = localStorage.getItem('access_token');

  useEffect(() => {
    const queryParams = new URLSearchParams(location.search);
    const bookId = queryParams.get('book_id');

    const completePurchase = async () => {
      try {
        const response = await axios.post(
          'http://localhost:8003/book-pub-buy/buy',
          { book_id: bookId },
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );
        console.log('Purchase confirmed:', response.data);
      } catch (error) {
        console.error('Error completing purchase:', error);
      }
    };

    if (bookId) {
      completePurchase();
    }
  }, [location, token]);

  return (
    <div className="success-page" style={{ textAlign: "center", marginTop: "100px" }}>
      <h1>✅ Payment Successful!</h1>
      <p>Your book has been unlocked.</p>
      <button onClick={() => navigate('/')}>Go to Home</button>
    </div>
  );
};

export default Success;