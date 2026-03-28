import os
import json
import psycopg2
from openai import OpenAI
from dotenv import load_dotenv

SIMILARITY_CUTOFF = .50
# CHUNK_LIMIT = 200 # not sure I want to implement this

def get_embedding(query):
    load_dotenv()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query)
    
	# data is an array, so [0] grabs the first and only element, since we are
    # only sending one string:
    return response.data[0].embedding

def extract_contents(results):
    return [ tuple[1] for tuple in results ]

def retrieve_most_similar(query):
    # get embedding for query
      # FOR RIGHT NOW, I'M NOT GOING TO CLEAN UP THE QUERY
      # THAT'S A TASK FOR ANOTHER DAY
    new_embedding = get_embedding(query)

    # Connect to Postgres
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="cpickard",
        database="lecture_rag"
    )
    cursor = conn.cursor()

    result = None

    try:
		# retrieve most similar
        cursor.execute("""
			SELECT lecture_title, content, 1 - (embedding::vector <=> %s::vector) AS similarity
			FROM data_chunks
            WHERE (1 - (embedding::vector <=> %s::vector)) > %s
            ORDER BY (1 - (embedding::vector <=> %s::vector)) DESC
		""", (new_embedding, new_embedding, SIMILARITY_CUTOFF, new_embedding))
        
		# extract the content from the cursor object
        raw_results = cursor.fetchall()
        # print(raw_results[-10:]) # prints content from LEAST relevant chunks that made it over the cutoff
        result = extract_contents(raw_results)
        # print(cursor.fetchone())
            
    except Exception as e:
        print("Error retrieving similar embedding:", e)

    finally:
        cursor.close()
        conn.close()

    return result # an array of strings

# test
# content = retrieve_most_similar('Tell me about the Ontological Argument')
# print(len(content)) # prints number of chunks grabbed.