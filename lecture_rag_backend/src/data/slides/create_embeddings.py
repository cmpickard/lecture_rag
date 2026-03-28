"""
Connect to postgres as cpickard connect to lecture_rag database

Create a new table -- slide_chunks:

psql

CREATE DATABASE lecture_rag

CREATE EXTENSION vector;

CREATE TABLE slide_chunks (
  id SERIAL PRIMARY KEY,
  course_title TEXT NOT NULL,
  lecture_title TEXT NOT NULL,
  slide_start INT NOT NULL,
  slide_end INT NOT NULL,
  content TEXT NOT NULL,
  embedding vector(1536)
);



Batch process the chunks of data in ./data/chunks.jsonl: 
- Send each chunk of OpenAI to be turned into an embedding
- INSERT the chunk data + embedding into our slide_chunks table

"""

import os
import json
from openai import OpenAI
import psycopg2
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_chunk_data():
    """Load slide deck chunks from jsonl file"""
    with open('./data/chunks_reformatted.jsonl', 'r') as file:
        return [json.loads(line) for line in file]

def generate_embeddings(batch_size=100):
    # Connect to Postgres
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="cpickard",
        database="lecture_rag"
    )
    cursor = conn.cursor()

    try:
        slide_chunks = load_chunk_data()
        
        # Process chapters in batches
        for i in range(0, len(slide_chunks), batch_size):
            batch = slide_chunks[i:i + batch_size]
            
            # Prepare batch data
            batch_contents = []
            batch_metadata = []
            
            for slide_chunk in batch:
                # Prepend course/lecture context so the embedding captures where this content is from
                content_str = (
                    f"Course: {slide_chunk['course_title']}\n"
                    f"Lecture: {slide_chunk['lecture_title']}\n"
                    f"{slide_chunk['content']}"
                )
                batch_contents.append(content_str)
                batch_metadata.append(slide_chunk)

            
            # Create embeddings for the entire batch
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=batch_contents
            )
            
            # Store each embedding with its metadata
            for j, embedding_data in enumerate(response.data):
                metadata = batch_metadata[j]
                embedding = embedding_data.embedding
                
                cursor.execute(
                    """INSERT INTO slide_chunks
                       (course_title, lecture_title, slide_start, slide_end, content, embedding)
                       VALUES (%s, %s, %s, %s, %s, %s::vector)""",
                    (metadata['course_title'], metadata['lecture_title'],
                     metadata['slide_start'], metadata['slide_end'],
                     metadata['content'], json.dumps(embedding))
                )
                print(f"Stored embedding for: {metadata['content'][:50]}...")
            
            print(f"Processed batch {i//batch_size + 1}/{(len(slide_chunks) + batch_size - 1)//batch_size}")

        conn.commit()
        print("All embeddings stored successfully!")

    except Exception as e:
        print("Error generating embeddings:", e)

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    generate_embeddings()