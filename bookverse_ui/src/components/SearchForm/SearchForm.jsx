import React, {useRef, useEffect} from 'react';
import {FaSearch} from "react-icons/fa";
import { useNavigate } from 'react-router-dom';
import { useGlobalContext } from '../../context.';
import "./SearchForm.css";

const SearchForm = () => {
  const {setTitle, setDescription, setAuthors, setSubjects, setResultTitle, setPaid, paid, setFree, free} = useGlobalContext();
  
  const titleRef = useRef('');
  const descriptionRef = useRef('');
  const authorsRef = useRef('');
  const subjectsRef = useRef('');

  const navigate = useNavigate();

  useEffect(() => titleRef.current.focus(), []);

  const handlePaidCheckboxChange = (e) => {
    setPaid(e.target.checked);
  };

  const handleFreeCheckboxChange = (e) => {
    setFree(e.target.checked);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const title = titleRef.current.value.trim();
    const description = descriptionRef.current.value.trim();
    const authors = authorsRef.current.value.trim();
    const subjects = subjectsRef.current.value.trim();

    const isAllEmpty = [title, description, authors, subjects].every(
      (value) => value === ''
    );

    if (isAllEmpty) {
      setResultTitle('Please enter something...');
    } else {
      setTitle(title);
      setDescription(description);
      setAuthors(authors);
      setSubjects(subjects);
    }

    navigate('/book');
  };

  return (
    <div className='search-form'>
      <div className='container'>
        <div className='search-form-content'>
          <form className='search-form' onSubmit={handleSubmit}>
            <div className='search-form-elem flex flex-sb bg-white m-2'>
              <input type = "text" className='form-control' placeholder='title' ref = {titleRef} />
            </div>
            <div className='search-form-elem flex flex-sb bg-white m-2'>
              <input type = "text" className='form-control' placeholder='description' ref = {descriptionRef} />
            </div>
            <div className='search-form-elem flex flex-sb bg-white m-2'>
              <input type = "text" className='form-control' placeholder='authors (comma seperated)' ref = {authorsRef} />
            </div>
            <div className='search-form-elem flex flex-sb bg-white m-2'>
              <input type = "text" className='form-control' placeholder='subjects (comma seperated)' ref = {subjectsRef} />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
              <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                <label className="form-check-label" htmlFor="paidCheckbox">
                  Paid
                </label>
                <input
                  style={{margin: 2}}
                  className="form-check-input"
                  type="checkbox"
                  id="paidCheckbox"
                  checked={paid || false} // avoid uncontrolled input warning
                  onChange={handlePaidCheckboxChange}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                <label className="form-check-label" htmlFor="paidCheckbox">
                  Free
                </label>
                <input
                  style={{margin: 2}}
                  className="form-check-input"
                  type="checkbox"
                  id="freeCheckbox"
                  checked={free || false} // avoid uncontrolled input warning
                  onChange={handleFreeCheckboxChange}
                />
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
              <button
                type="submit"
                className="btn btn-primary d-flex justify-content-center align-items-center"
                onClick={handleSubmit}
                style={{ width: '100px', height: '48px', padding: 0, margin: 10 }}
              >
                <FaSearch style={{ color: 'white' }} size={24} />
                <h2>Search</h2>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

export default SearchForm