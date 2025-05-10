import React, { useState, useEffect } from 'react';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import { useNavigate } from 'react-router-dom';
import axios from "axios";
import {auth_link} from "../../backend_links.js";


function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const tokenVerify = async() => {

    const token = localStorage.getItem('access_token');
    const tokenExpiration = localStorage.getItem('expire');

    if (token && tokenExpiration) {
      const expirationTime = parseInt(tokenExpiration);
      if (Date.now() < expirationTime) {
        // Token is still valid, set it in axios headers
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        try {
          // Send a request to verify the token with the backend
          const response = await axios.get(`${auth_link}/verify-token`);

          if(response.status == 200){
            console.log('token verified for user:', response.user_id);
            // Redirect to home page
            navigate("/");
            // Reload the page
            window.location.reload();
          }
        } catch (error) {
          console.error('Error verifying token:', error);
        }
      }
    }
  }

  useEffect(() => {
    tokenVerify()
  }, [navigate]);

  const handleEmailChange = (e) => {
    setEmail(e.target.value);
  };

  const handlePasswordChange = (e) => {
    setPassword(e.target.value);
  };

  const isValidEmail = (email) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const login = async() => {
    try{
      const response = await axios.post(`${auth_link}/login`, {
        email: email,
        password: password,
      });

      console.log('Login response:', response);

      const { access_token, expire } = response.data;
      
      // Store token and expiration time in localStorage
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('expire', expire);
      
      // Set token in axios headers
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      console.log('Login successful!');
      
      // Redirect to home page
      navigate("/");

      // Reload the page
      window.location.reload();
    } catch(err){
      console.log(err)
      alert("wrong password or email")
    }
    
  }

  const handleButtonClick = async() => {
    // Perform login logic, and if successful, store a cookie
    console.log('email:', email);
    console.log('password:', password);

    if (!isValidEmail(email)) {
      alert('Please enter a valid email address.');
      return;
    }

    try {
      login();
    } catch (error) {
      console.error('Error:', error);
    }
    
  };

  return (
    <div className="d-flex justify-content-center align-items-center vh-100">
      <Form style={{ width: '400px', padding: '20px', borderRadius: '10px', boxShadow: '0 0 10px rgba(0, 0, 0, 0.1)' }}>
        <Form.Group className="mb-3" controlId="exampleForm.ControlInput1">
          <Form.Label>Email</Form.Label>
          <Form.Control
            type="email"
            placeholder="email@gmail.com"
            value={email}
            onChange={handleEmailChange}
          />
        </Form.Group>
        <Form.Group className="mb-3" controlId="exampleForm.ControlInput1">
          <Form.Label>Password</Form.Label>
          <Form.Control
            type="password"
            placeholder="Password"
            value={password}
            onChange={handlePasswordChange}
          />
        </Form.Group>
        <div style={{ display: 'flex' }}>
          <p>Don't have an account?</p>
          <a href="/register" style={{ marginLeft: '1rem', color: 'blue', textDecoration: 'underline'}}>Register</a>
        </div>
        <Button variant="secondary" onClick={handleButtonClick}>
          Login
        </Button>{' '}
      </Form>
    </div>
  );
}

export default Login;