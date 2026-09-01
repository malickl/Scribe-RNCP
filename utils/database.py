from psycopg2.pool import ThreadedConnectionPool
import os
from dotenv import load_dotenv
from contextlib import contextmanager
import json

load_dotenv()

# ThreadedConnectionPool car run_pipeline() touche la DB depuis des threads
# de fond en parallèle des requêtes Flask. Créé à la première utilisation
# (pas à l'import) : importer ce module ne doit pas exiger une base
# accessible (tests, CI), et une indisponibilité momentanée de la base au
# démarrage du process ne doit pas empêcher l'application de démarrer.
_pool = None


def _get_pool():
    global _pool
    if _pool is None:
        _pool = ThreadedConnectionPool(1, 10, dsn=os.getenv("DATABASE_PUBLIC_URL"))
    return _pool


@contextmanager
def get_cursor(commit=False):
    pool = _get_pool()
    conn = pool.getconn()
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
        pool.putconn(conn)


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


def delete_user(id_user):
    """Supprime définitivement un utilisateur sans supprimer ses contenus."""
    with get_cursor(commit=True) as cur:
        cur.execute("DELETE FROM users WHERE id_user = %s", (id_user,))


def _normalize_actions(actions):
    """Les réunions/dictaphones analysés avant l'ajout de la case à cocher
    ont des actions stockées comme de simples chaînes ; on les remet à niveau
    à la lecture plutôt que de migrer les données existantes."""
    return [
        action if isinstance(action, dict) else {"texte": action, "fait": False}
        for action in actions
    ]


def get_user_meetings(id_user):
    with get_cursor() as cur:
        cur.execute("""
            SELECT DISTINCT r.id_reunion, r.titre, r.date, r.theme, r.categorie, r.humeur, r.resume, r.actions
            FROM reunions r
            LEFT JOIN reunion_participants rp ON rp.id_reunion = r.id_reunion
            WHERE r.id_user = %s OR rp.id_user = %s
            ORDER BY r.date DESC
        """, (id_user, id_user))
        rows = cur.fetchall()

    result = []
    for row in rows:
        row = list(row)
        row[7] = _normalize_actions(json.loads(row[7])) if row[7] else []
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
        row[7] = _normalize_actions(json.loads(row[7])) if row[7] else []
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


def toggle_action(id_user, table, row_id, index):
    """Coche/décoche l'action à `index` pour la réunion/le dictaphone donné.
    Accès vérifié explicitement (propriétaire, ou participant pour une
    réunion partagée) plutôt que de faire confiance à l'identifiant seul."""
    column_id = "id_reunion" if table == "reunions" else "id_dictaphone"

    with get_cursor(commit=True) as cur:
        if table == "reunions":
            cur.execute("""
                SELECT actions FROM reunions r
                LEFT JOIN reunion_participants rp ON rp.id_reunion = r.id_reunion
                WHERE r.id_reunion = %s AND (r.id_user = %s OR rp.id_user = %s)
            """, (row_id, id_user, id_user))
        else:
            cur.execute(f"""
                SELECT actions FROM {table}
                WHERE {column_id} = %s AND id_user = %s
            """, (row_id, id_user))

        row = cur.fetchone()
        if not row or not row[0]:
            return

        actions = _normalize_actions(json.loads(row[0]))
        if not 0 <= index < len(actions):
            return

        actions[index]["fait"] = not actions[index]["fait"]

        cur.execute(f"""
            UPDATE {table}
            SET actions = %s
            WHERE {column_id} = %s
        """, (json.dumps(actions), row_id))


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


def get_all_reunion_keys():
    """(titre, date) -> id_reunion pour TOUTES les réunions, tous utilisateurs
    confondus : sert à détecter qu'un bot a déjà été envoyé pour un événement
    donné par n'importe qui, sans colonne google_event_id dédiée."""
    with get_cursor() as cur:
        cur.execute("SELECT titre, date, id_reunion FROM reunions")
        rows = cur.fetchall()
    return {
        (titre, date.strftime('%Y-%m-%dT%H:%M:%S')): id_reunion
        for titre, date, id_reunion in rows if date
    }


def insert_reunion(id_user, titre, date, recall_bot_id, participant_emails=None):
    """Crée la réunion, rattache son expéditeur, et rattache automatiquement
    tout autre invité (participant_emails) qui a déjà un compte Scribe —
    ils recevront le compte-rendu sur leur dashboard sans rien faire."""
    with get_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO reunions (id_user, titre, date, recall_bot_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id_reunion
        """, (id_user, titre, date, recall_bot_id))
        id_reunion = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO reunion_participants (id_reunion, id_user)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, (id_reunion, id_user))

        if participant_emails:
            cur.execute("""
                SELECT id_user FROM users WHERE email = ANY(%s)
            """, (participant_emails,))
            for (autre_id_user,) in cur.fetchall():
                cur.execute("""
                    INSERT INTO reunion_participants (id_reunion, id_user)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                """, (id_reunion, autre_id_user))

        return id_reunion
