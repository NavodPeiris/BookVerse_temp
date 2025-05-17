import React, {useState, useEffect} from 'react';
import { useParams } from 'react-router-dom';
import Loading from "../Loader/Loader";
import coverImg from "../../images/cover_not_found.jpg";
import "./BookDetails.css";
import { FaArrowLeft, FaShoppingCart, FaDownload, FaHeart, FaStar, FaBookOpen } from "react-icons/fa";
import { useNavigate } from 'react-router-dom';
import axios from "axios";
import { book_catalog_link, minio_link } from '../../backend_links';

const BookDetails = () => {
  const {id} = useParams();
  const [loading, setLoading] = useState(false);
  const [book, setBook] = useState(null);
  const navigate = useNavigate();
  const downloadUrl = `${book_catalog_link}/download_book/${id}.pdf`
  const token = localStorage.getItem('access_token');

  const setBookDetails = async() => {
    try{
      const response = await axios.get(`${book_catalog_link}/works/${id}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      const data = response.data;
      console.log(data);

      if(data){
        const {description, title, cover_image_available, subject_places, subject_times, subjects, paid, like_count, user_liked, rate} = data;
        const newBook = {
          description: description ? description : "No description found",
          title: title,
          cover_img: cover_image_available ? `${minio_link}/book-cover-images/${id}.jpg` : coverImg,
          subject_places: subject_places ? subject_places.join(", ") : "No subject places found",
          subject_times : subject_times ? subject_times.join(", ") : "No subject times found",
          subjects: subjects ? subjects.join(", ") : "No subjects found",
          paid: paid,
          like_count: like_count,
          user_liked: user_liked,
          rate: rate
        };
        setBook(newBook);
      } else {
        setBook(null);
      }
      setLoading(false);
    } catch(error){
      console.log(error);
      setLoading(false);
    }
  }

  useEffect(() => {
    setLoading(true);
    setBookDetails();
  }, [id]);

  if(loading) return <Loading />;

  const handleLike = async() => {
    try {
      const response = await axios.post(
        `${book_catalog_link}/like/${id}`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      if (response.status === 200 && book) {
        setLoading(true);
        setBookDetails();
      }
    } catch (error) {
      console.error("Error liking the book:", error);
    }
  }

  return (
    <section className='book-details'>
      <div className='container'>
        <button type='button' className='flex flex-c back-btn' onClick={() => navigate("/book")}>
          <FaArrowLeft size = {22} />
          <span className='fs-18 fw-6'>Go Back</span>
        </button>

        <div className='book-details-content grid'>
          <div className='book-details-img'>
            <img src = {book?.cover_img} alt = "cover img" />
            <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center', margin: '5px'}}>

              <button type='button' className='flex flex-c back-btn' disabled={!book?.paid}>
                <FaShoppingCart size={24}/>
              </button>

              <button type='button' className='flex flex-c back-btn' disabled={book?.paid} onClick={() => {if (!book?.paid) window.open(downloadUrl, "_blank");}}>
                <FaDownload size={24} />
              </button>
              
              <button type='button' className='flex flex-c back-btn' disabled={book?.paid} onClick={() => navigate(`/bookflip/${id}`)}>
                <FaBookOpen size={24} />
              </button>

              <button type='button' className='flex flex-c back-btn' disabled={book?.paid} onClick={handleLike}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <FaHeart size={24} style={{ color: book?.user_liked? "var(--purple-color)" : "" }}/>
                  <span>{book?.like_count}</span>
                </div>
              </button>

              <button type='button' className='flex flex-c back-btn' disabled={book?.paid}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <FaStar size={24} />
                  <span>{book?.rate}</span>
                </div>
              </button>

            </div>
          </div>
          <div className='book-details-info'>
            <div className='book-details-item title'>
              <span className='fw-6 fs-24'>{book?.title}</span>
            </div>
            <div className='book-details-item description'>
              <span>{book?.description}</span>
            </div>
            <div className='book-details-item'>
              <span className='fw-6'>Subject Places: </span>
              <span className='text-italic'>{book?.subject_places}</span>
            </div>
            <div className='book-details-item'>
              <span className='fw-6'>Subject Times: </span>
              <span className='text-italic'>{book?.subject_times}</span>
            </div>
            <div className='book-details-item'>
              <span className='fw-6'>Subjects: </span>
              <span>{book?.subjects}</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default BookDetails