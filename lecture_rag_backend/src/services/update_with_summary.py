import psycopg2

def update_with_summary(summary, uuid):
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
          SET summary = %s
          WHERE id = %s;
          """, (summary, uuid))
      conn.commit()

  except Exception as e:
      print("Error updating history:", e)

  finally:
      cursor.close()
      conn.close()

  return