CREATE TABLE data_chunks (
    id serial PRIMARY KEY,
    lecture_title text NOT NULL,
    content text NOT NULL,
    embedding vector(1536)
);