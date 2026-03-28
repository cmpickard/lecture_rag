"""
Connect to postgres as cpickard connect to lecture_rag database


data_chunks table schema (
  id SERIAL PRIMARY KEY,
  lecture_title TEXT NOT NULL,
  content TEXT NOT NULL,
  embedding vector(1536)
);



Batch process the chunks of data in /data/q_and_a/qa_chunks.jsonl: 
- Send each chunk of OpenAI to be turned into an embedding
- INSERT the chunk data + embedding into our data_chunks table

"""

import os
import json
from openai import OpenAI
import psycopg2
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_chunk_data():
    """Load chunks from JSONL file"""
    path = os.path.join(os.path.dirname(__file__), 'qa_chunks.jsonl')
    with open(path, 'r') as file:
        return [json.loads(line) for line in file if line.strip()]

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
        data_chunks = load_chunk_data()
        
        # Process chapters in batches
        for i in range(0, len(data_chunks), batch_size):
            batch = data_chunks[i:i + batch_size]
            
            # Prepare batch data
            batch_contents = []
            batch_metadata = []
            
            for data_chunk in batch:
                # Prepend course/lecture context so the embedding captures where this content is from
                content_str = (
                    f"Lecture: {data_chunk['lecture_title']}\n"
                    f"{data_chunk['content']}"
                )
                batch_contents.append(content_str)
                batch_metadata.append(data_chunk)

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
                    """INSERT INTO data_chunks
                       (lecture_title, content, embedding)
                       VALUES (%s, %s, %s::vector)""",
                    (metadata['lecture_title'],
                     metadata['content'], json.dumps(embedding))
                )
                print(f"Stored embedding for: {metadata['content'][:50]}...")
            
            print(f"Processed batch {i//batch_size + 1}/{(len(data_chunks) + batch_size - 1)//batch_size}")

        conn.commit()
        print("All embeddings stored successfully!")

    except Exception as e:
        conn.rollback()
        print("Error generating embeddings:", e)

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    generate_embeddings()