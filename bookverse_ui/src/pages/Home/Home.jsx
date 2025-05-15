import React, { useState, useEffect } from 'react';
import Header from '../../components/Header/Header';
import { Outlet, useNavigate } from 'react-router-dom';

const Home = () => {
  const navigate = useNavigate();

  const tokenVerify = async() => {
    const token = localStorage.getItem('access_token');
    const tokenExpiration = localStorage.getItem('expire');

    const today = new Date().toISOString().split('T')[0]; // format: YYYY-MM-DD
    const expirationDate = new Date(tokenExpiration).toISOString().split('T')[0];

    if (expirationDate < today) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('expire');
      console.log('Token expired and removed.');
      navigate("/login");
    }

    if (token && tokenExpiration) {
      console.log("user logged in")
    }
    else {
      navigate("/login");
    }
  }
  
  useEffect(() => {
    tokenVerify()
  }, [navigate]);

  return (
    <main>
        <Header />
        <Outlet />
    </main>
  )
}

export default Home
