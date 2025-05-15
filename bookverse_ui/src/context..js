import React, {useState, useContext, useEffect} from 'react';
import { useCallback } from 'react';
import axios from "axios";
import { book_catalog_link } from './backend_links';
const AppContext = React.createContext();

const AppProvider = ({children}) => {
    const [title, setTitle] = useState(null);
    const [description, setDescription] = useState(null);
    const [authors, setAuthors] = useState(null);
    const [subjects, setSubjects] = useState(null);
    const [paid, setPaid] = useState(null);
    const [free, setFree] = useState(null);

    const [books, setBooks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [resultTitle, setResultTitle] = useState("");

    const fetchBooks = useCallback(async() => {
        setLoading(true);
        const body = {}

        if (title !== null && title !== "") body.title = title;
        if (description !== null && description !== "") body.description = description;
        if (authors !== null && authors !== "") body.authors = authors;
        if (subjects !== null && subjects !== "") body.subjects = subjects;
        if (paid !== null && paid !== "") body.paid = paid;
        if (free !== null && free !== "") body.free = free;

        console.log("request body:", body)
        
        try{
            const token = localStorage.getItem('access_token');
            const response = await axios.post(`${book_catalog_link}/search`,
            body,
            {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            }
            );
            const docs = response.data;

            console.log(docs);

            if(docs){
                const newBooks = docs.slice(0, 20).map((bookSingle) => {
                    const {key, author_name, cover_i, edition_count, first_publish_year, title} = bookSingle;
                    console.log(key)
                    return {
                        id: key,
                        author: author_name,
                        cover_id: cover_i,
                        edition_count: edition_count,
                        first_publish_year: first_publish_year,
                        title: title
                    }
                });

                setBooks(newBooks);

                if(newBooks.length > 1){
                    setResultTitle("Your Search Result");
                } else {
                    setResultTitle("No Search Result Found!")
                }
            } else {
                setBooks([]);
                setResultTitle("No Search Result Found!");
            }
            setLoading(false);
        } catch(error){
            console.log(error);
            setLoading(false);
        }
    }, [title, description, authors, subjects]);

    useEffect(() => {
        fetchBooks();
    }, [title, description, authors, subjects, fetchBooks]);

    return (
        <AppContext.Provider value = {{
            loading, books, setTitle, setDescription, setAuthors, setSubjects, setPaid, setFree, paid, free, resultTitle, setResultTitle,
        }}>
            {children}
        </AppContext.Provider>
    )
}

export const useGlobalContext = () => {
    return useContext(AppContext);
}

export {AppContext, AppProvider};