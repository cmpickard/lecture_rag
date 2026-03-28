import psycopg2
import json

def retrieve_history(uuid, query):
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        user='cpickard',
        database='lecture_rag'
    )

    cursor = conn.cursor()

    result = None

    try:
        if uuid != '':
            cursor.execute("""
                SELECT history
                FROM conversations
                WHERE id = %s
            """, (uuid,))
            
            row = cursor.fetchone()
            
            if row:
                result = row[0]

        else:
            cursor.execute(
                "INSERT INTO conversations (history) VALUES (%s) RETURNING id;",
                (json.dumps([{"role": "user", "content": query}]),)
            )
            result = cursor.fetchone()[0]
            conn.commit()
            
    except Exception as e:
        print("Error retrieving history:", e)

    finally:
        cursor.close()
        conn.close()

    return result # the history JSONB value, or UUID 

# test
# history = retrieve_history('9f8cd020-14c0-4bda-b62f-84c17d168bd3')
# print(history)

# uuid = retrieve_history('', "Tell me about the Ontological Argument.")
# print(uuid)