CREATE TABLE IF NOT EXISTS likes (
    user_id INT REFERENCES users(id),
    book_id VARCHAR(100),
    PRIMARY KEY (user_id, book_id)
);