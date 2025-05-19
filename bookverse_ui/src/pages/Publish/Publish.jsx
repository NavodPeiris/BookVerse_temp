import React, {useState, useEffect} from "react";
import './Publish.css';
import { book_pub_buy_link } from "../../backend_links";
import axios from "axios";

const Publish = () => {

  const [first_publish_year, setFirstPubYear] = useState(0);
  const [title, setTitle] = useState(null);
  const [subtitle, setSubTitle] = useState(null);
  const [cover_image_available, setCoverImageAvailable] = useState(null);
  const [authors, setAuthors] = useState(null);
  const [subjects, setSubjects] = useState(null);
  const [subject_places, setSubjectPlaces] = useState(null);
  const [subject_times, setSubjectTimes] = useState(null);
  const [description, setDescription] = useState(null);
  const [edition_count, setEditionCount] = useState(null);
  const [price, setPrice] = useState(null);
  const [doc, setDoc] = useState(null);
  const [img, setImg] = useState(null); // only set if cover image available

  const token = localStorage.getItem('access_token');

  // TODO: handle rating (abiman)
  const handlePublish = async() => {
    try {
      const response = await axios.post(
        `${book_pub_buy_link}/publish`,
        {
          first_publish_year: first_publish_year,
          title: title,
          subtitle: subtitle,
          cover_image_available: cover_image_available,
          authors: authors,
          subjects: subjects,
          subject_places: subject_places,
          subject_times: subject_times,
          description: description,
          edition_count: edition_count,
          price: price,
          doc: doc,
          img: img
        },
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

    } catch (error) {
      console.error("Error liking the book:", error);
    }
  }

  return (
    <section className='about'>
      <div className='container'>
        <div className='section-title'>
          <h2>Publish</h2>
        </div>

        <div className='about-content grid'>
          <h2>work in progress</h2>
        </div>
      </div>
    </section>
  )
}

export default Publish
