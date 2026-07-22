import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_PUBLIC_URL"))
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id_user UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        nom VARCHAR(100),
        email VARCHAR(100) UNIQUE NOT NULL,
        consentement_date TIMESTAMP
    )
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS reunions (
        id_reunion UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        id_user UUID REFERENCES users(id_user) ON DELETE CASCADE,
        titre VARCHAR(200),
        date TIMESTAMP,
        duree_secondes INTEGER,
        participants TEXT,
        theme TEXT,
        categorie VARCHAR(50),
        humeur VARCHAR(20),
        resume TEXT,
        actions TEXT,
        recall_bot_id VARCHAR(100)
    )
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS dictaphones (
        id_dictaphone UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        id_user UUID REFERENCES users(id_user) ON DELETE CASCADE,
        titre VARCHAR(200),
        date TIMESTAMP,
        duree_secondes INTEGER,
        theme TEXT,
        categorie VARCHAR(50),
        humeur VARCHAR(20),
        resume TEXT,
        actions TEXT
    )
""")

conn.commit()
cur.close()
conn.close()
print("Tables créées avec succès.")