import psycopg2

def conversation_deletion(uuid):
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        user='cpickard',
        database='lecture_rag'
    )

    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM conversations
            WHERE id = %s;
            """, (uuid,))
        conn.commit()
    except Exception as e:
        print("Error updating history:", e)

    finally:
        cursor.close()
        conn.close()

    return