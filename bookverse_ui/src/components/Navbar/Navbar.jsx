import React, {useState} from 'react';
import { Link, useNavigate } from 'react-router-dom';
import "./Navbar.css";
import logoImg from "../../images/logo.png";
import {HiOutlineMenuAlt3} from "react-icons/hi";

const Navbar = () => {
  const [toggleMenu, setToggleMenu] = useState(false);
  const handleNavbar = () => setToggleMenu(!toggleMenu);
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('expire');
    console.log('Token removed.');
    navigate("/login");
  }

  return (
    <nav className='navbar' id = "navbar">
      <div className='container navbar-content flex'>
        <div className='brand-and-toggler flex flex-sb'>
          <Link to = "/" className='navbar-brand flex'>
            <img src = {logoImg} alt = "site logo" />
            <span className='text-uppercase fw-7 fs-24 ls-1'>BookVerse</span>
          </Link>
          <button type = "button" className='navbar-toggler-btn' onClick={handleNavbar}>
            <HiOutlineMenuAlt3 size = {35} style = {{
              color: `${toggleMenu ? "#fff" : "#010101"}`
            }} />
          </button>
        </div>

        <div className={toggleMenu ? "navbar-collapse show-navbar-collapse" : "navbar-collapse"}>
          <ul className = "navbar-nav-list">
            <li className='nav-item'>
              <Link to = "book" className='nav-link text-uppercase text-black fs-22 fw-6 ls-1'>Home</Link>
            </li>
            <li className='nav-item'>
              <Link to = "about" className='nav-link text-uppercase text-black fs-22 fw-6 ls-1'>about</Link>
            </li>
            <li className='nav-item'>
              <Link to = "publish" className='nav-link text-uppercase text-black fs-22 fw-6 ls-1'>publish</Link>
            </li>
            <button
              type="submit"
              className="nav-link text-uppercase text-black fs-18 fw-6 ls-1 ms-3 mt-1"
              onClick={handleLogout}
              
            >
              <h2>Logout</h2>
            </button>
          </ul>
        </div>
      </div>
    </nav>
  )
}

export default Navbar