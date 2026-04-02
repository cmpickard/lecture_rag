import psycopg2
import json


def replace_history(summary: str, uuid: str) -> None:
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        user='cpickard',
        database='lecture_rag'
    )

    cursor = conn.cursor()

    try:
        compacted = [{"role": "system", "content": f"Previous conversation summary: {summary}"}]
        cursor.execute("""
            UPDATE conversations
            SET llm_context = %s
            WHERE id = %s;
        """, (json.dumps(compacted), uuid))
        conn.commit()

    except Exception as e:
        print("Error replacing history:", e)

    finally:
        cursor.close()
        conn.close()
