import psycopg2


def cache_write(query_embedding, query_text, response_text, dialogue_mode):
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="cpickard",
        database="lecture_rag"
    )
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO response_cache (query_embedding_vector, query_text, response_text, dialogue_mode)
            VALUES (%s::vector, %s, %s, %s)
        """, (query_embedding, query_text, response_text, dialogue_mode))
        conn.commit()

    except Exception as e:
        print("Error writing to cache:", e)

    finally:
        cursor.close()
        conn.close()
