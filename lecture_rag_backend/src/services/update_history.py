import psycopg2
import json

def update_history(role, content, uuid):
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        user='cpickard',
        database='lecture_rag'
    )

    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE conversations
            SET history = history || %s
            WHERE id = %s;
            """, (json.dumps([{"role": role, "content": content}]), uuid))
        conn.commit()
    except Exception as e:
        print("Error updating history:", e)

    finally:
        cursor.close()
        conn.close()

    return

# test
# update_history('user', 'Tell me about yourself', '9f8cd020-14c0-4bda-b62f-84c17d168bd3')
