"""
Fonctions d'accès à PostgreSQL. Centralise les requêtes pour éviter de les dupliquer
dans chaque route.
"""

def get_or_create_user(email, nom):
    """
    Cherche un utilisateur par email. Le crée s'il n'existe pas. Retourne son id_user.
    """
    pass


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
