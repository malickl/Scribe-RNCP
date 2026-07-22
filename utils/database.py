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


def insert_reunion(id_user, titre, date, participants, recall_bot_id):
    """
    Crée une ligne dans reunions avec les colonnes d'analyse vides. Retourne id_reunion.
    """
    pass


def update_analyse(table, row_id, report):
    """
    Met à jour une ligne (reunions ou dictaphones) avec le résultat de l'analyse LLM.
    """
    pass
