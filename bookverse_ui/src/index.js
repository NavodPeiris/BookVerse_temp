import React from 'react';
import ReactDOM from 'react-dom/client';
import {
  BrowserRouter, Routes, Route
} from 'react-router-dom';
import { AppProvider } from './context.';
import './index.css';

import Home from './pages/Home/Home';
import About from "./pages/About/About";
import BookList from "./components/BookList/BookList";
import BookDetails from "./components/BookDetails/BookDetails";
import Login from './pages/User/Login';
import Register from './pages/User/Register';
import BookFlip from './components/BookDetails/BookFlip';
import Publish from './pages/Publish/Publish';
import Success from './pages/SuccessPay/SuccessPay';
import Cancel from './pages/CancelPay/CancelPay';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <AppProvider>
    <BrowserRouter>
      <Routes>
        <Route path = "/" element = {<Home />}>
          <Route path = "about" element = {<About />} />
          <Route path = "publish" element = {<Publish />} />
          <Route path = "book" element = {<BookList />} />
          <Route path = "/book/:id" element = {<BookDetails />} />
        </Route>
        <Route path = "/bookflip/:id" element = {<BookFlip/>} />
        <Route path = "/login" element = {<Login/>} />
        <Route path = "/register" element = {<Register/>} />
        <Route path = "/success" element = {<Success/>} />
        <Route path = "/cancel" element = {<Cancel/>} />
      </Routes>
    </BrowserRouter>
  </AppProvider>
);

