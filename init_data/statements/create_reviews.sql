CREATE TABLE IF NOT EXISTS reviews (
    user_id INT REFERENCES users(id),
    book_id VARCHAR(100),
    review VARCHAR(300),
    rate INT,
    PRIMARY KEY (user_id, book_id)
);