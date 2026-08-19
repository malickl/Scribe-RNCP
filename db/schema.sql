-- Schéma de référence, identique à ce que crée init_db.py
-- Utile pour visualiser la structure sans lancer de code Python

CREATE TABLE users (
    id_user UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nom VARCHAR(100),
    email VARCHAR(100) UNIQUE NOT NULL,
    consentement_date TIMESTAMP
);

CREATE TABLE reunions (
    id_reunion UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_user UUID REFERENCES users(id_user) ON DELETE SET NULL,
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
);

CREATE TABLE dictaphones (
    id_dictaphone UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_user UUID REFERENCES users(id_user) ON DELETE SET NULL,
    titre VARCHAR(200),
    date TIMESTAMP,
    duree_secondes INTEGER,
    theme TEXT,
    categorie VARCHAR(50),
    humeur VARCHAR(20),
    resume TEXT,
    actions TEXT
);

-- Participants Scribe d'une réunion visio, au-delà de celui qui a envoyé le
-- bot (reunions.id_user). Permet à plusieurs utilisateurs de recevoir le
-- même compte-rendu sans envoyer chacun leur propre bot.
CREATE TABLE reunion_participants (
    id_reunion UUID REFERENCES reunions(id_reunion) ON DELETE CASCADE,
    id_user UUID REFERENCES users(id_user) ON DELETE CASCADE,
    PRIMARY KEY (id_reunion, id_user)
);
