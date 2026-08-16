import psycopg2
from psycopg2.pool import ThreadedConnectionPool
import os
from dotenv import load_dotenv
from contextlib import contextmanager
import json

load_dotenv()

# ThreadedConnectionPool car run_pipeline() touche la DB depuis des threads
# de fond en parallèle des requêtes Flask.
_pool = ThreadedConnectionPool(1, 10, dsn=os.getenv("DATABASE_PUBLIC_URL"))


@contextmanager
def get_cursor(commit=False):
    conn = _pool.getconn()
    try:
        cur = conn.cursor()
        yield cur
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        _pool.putconn(conn)


def get_or_create_user(email, nom):
    with get_cursor(commit=True) as cur:
        cur.execute("SELECT id_user FROM users WHERE email = %s", (email,))
        row = cur.fetchone()

        if row:
            return row[0]

        cur.execute("""
            INSERT INTO users (nom, email)
            VALUES (%s, %s)
            RETURNING id_user
        """, (nom, email))
        return cur.fetchone()[0]


def get_user(id_user):
    with get_cursor() as cur:
        cur.execute("SELECT nom, email FROM users WHERE id_user = %s", (id_user,))
        row = cur.fetchone()
        return {"nom": row[0], "email": row[1]} if row else None


def check_consent(id_user):
    with get_cursor() as cur:
        cur.execute("SELECT consentement_date FROM users WHERE id_user = %s", (id_user,))
        row = cur.fetchone()
        return row is not None and row[0] is not None


def record_consent(id_user):
    with get_cursor(commit=True) as cur:
        cur.execute("""
            UPDATE users
            SET consentement_date = NOW()
            WHERE id_user = %s
        """, (id_user,))


def get_user_meetings(id_user):
    with get_cursor() as cur:
        cur.execute("""
            SELECT id_reunion, titre, date, theme, categorie, humeur, resume, actions
            FROM reunions WHERE id_user = %s ORDER BY date DESC
        """, (id_user,))
        rows = cur.fetchall()

    result = []
    for row in rows:
        row = list(row)
        row[7] = json.loads(row[7]) if row[7] else []
        result.append(row)
    return result


def get_user_recordings(id_user):
    with get_cursor() as cur:
        cur.execute("""
            SELECT id_dictaphone, titre, date, theme, categorie, humeur, resume, actions
            FROM dictaphones
            WHERE id_user = %s
            ORDER BY date DESC
        """, (id_user,))
        rows = cur.fetchall()

    result = []
    for row in rows:
        row = list(row)
        row[7] = json.loads(row[7]) if row[7] else []
        result.append(row)
    return result


def insert_dictaphone(id_user, titre):
    with get_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO dictaphones (id_user, titre, date)
            VALUES (%s, %s, NOW())
            RETURNING id_dictaphone
        """, (id_user, titre))
        return cur.fetchone()[0]


def rename_item(id_user, table, row_id, titre):
    column_id = "id_reunion" if table == "reunions" else "id_dictaphone"

    with get_cursor(commit=True) as cur:
        cur.execute(f"""
            UPDATE {table}
            SET titre = %s
            WHERE {column_id} = %s AND id_user = %s
        """, (titre, row_id, id_user))


def update_analysis(table, row_id, report):
    column_id = "id_reunion" if table == "reunions" else "id_dictaphone"

    with get_cursor(commit=True) as cur:
        cur.execute(f"""
            UPDATE {table}
            SET theme = %s, categorie = %s, humeur = %s, resume = %s, actions = %s
            WHERE {column_id} = %s
        """, (
            report["theme"],
            report["categorie"],
            report["humeur"],
            report["resume"],
            json.dumps(report["actions"]),
            row_id
        ))


def get_reunion_by_bot_id(bot_id):
    with get_cursor() as cur:
        cur.execute("SELECT id_reunion FROM reunions WHERE recall_bot_id = %s", (bot_id,))
        row = cur.fetchone()
        return row[0] if row else None


def get_bot_event_keys(id_user):
    """(titre, date) des réunions déjà envoyées à un bot, pour détecter les doublons
    sans colonne dédiée : on réutilise titre+date, déjà stockés tels quels."""
    with get_cursor() as cur:
        cur.execute("SELECT titre, date FROM reunions WHERE id_user = %s", (id_user,))
        rows = cur.fetchall()
    return {(titre, date.strftime('%Y-%m-%dT%H:%M:%S')) for titre, date in rows if date}


def insert_reunion(id_user, titre, date, recall_bot_id):
    with get_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO reunions (id_user, titre, date, recall_bot_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id_reunion
        """, (id_user, titre, date, recall_bot_id))
        return cur.fetchone()[0]
