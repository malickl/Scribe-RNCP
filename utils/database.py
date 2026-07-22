import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def get_or_create_user(email, nom):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id_user FROM users WHERE email = %s", (email,))
    row = cur.fetchone()

    if row:
        id_user = row[0]
    else:
        cur.execute("""
            INSERT INTO users (nom, email)
            VALUES (%s, %s)
            RETURNING id_user
        """, (nom, email))
        id_user = cur.fetchone()[0]
        conn.commit()

    cur.close()
    conn.close()
    return id_user


def check_consent(id_user):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT consentement_date FROM users WHERE id_user = %s", (id_user,))
    row = cur.fetchone()

    cur.close()
    conn.close()
    return row is not None and row[0] is not None


def record_consent(id_user):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET consentement_date = NOW()
        WHERE id_user = %s
    """, (id_user,))
    conn.commit()

    cur.close()
    conn.close()

def get_user_meetings(id_user):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id_reunion, titre, date, theme, categorie, humeur, resume, actions
        FROM reunions
        WHERE id_user = %s
        ORDER BY date DESC
    """, (id_user,))
    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows 