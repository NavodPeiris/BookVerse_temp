import React, { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { book_pub_buy_link } from '../../backend_links'; 

const Success = () => {
  const location = useLocation();

  const navigate = useNavigate();
  const token = localStorage.getItem('access_token');

  const queryParams = new URLSearchParams(location.search);
  const bookId = queryParams.get('book_id');

  useEffect(() => {
    const completePurchase = async () => {
      try {
        const response = await axios.post(
          `${book_pub_buy_link}/buy`,
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
      <button onClick={() => navigate(`/book/${bookId}`)}>Go to Book</button>
    </div>
  );
};

export default Success;