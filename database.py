import psycopg2
import psycopg2.extras
from config import Config

def get_connection():
    return psycopg2.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        dbname=Config.DB_NAME,
        port=Config.DB_PORT,
        sslmode='require'
    )

def query(sql, params=None, fetchone=False, fetchall=False, commit=False):
    conn = get_connection()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params or ())
        if commit:
            conn.commit()
            return True
        if fetchone:
            return cur.fetchone()
        if fetchall:
            return cur.fetchall()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
