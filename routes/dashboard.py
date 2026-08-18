"""
Lot 4 : Données & restitution
Tableau de bord, filtres, suppression de compte.
"""

from collections import Counter
from datetime import datetime, timedelta
from flask import Blueprint, session, redirect, url_for, render_template, request
from utils.database import (
    check_consent,
    record_consent,
    get_user_meetings,
    get_user_recordings,
    get_user,
    rename_item
)

dashboard_bp = Blueprint("dashboard", __name__)

TABLES_RENOMMABLES = {"reunions", "dictaphones"}


def _stats(meetings, recordings):
    categories = Counter()
    humeurs = Counter()

    for _, _, _, theme, categorie, humeur, resume, _ in meetings + recordings:
        if not resume:
            continue

        if categorie:
            categories[categorie] += 1

        if humeur:
            humeurs[humeur] += 1

    top_categorie = categories.most_common(1)[0][0] if categories else None
    top_humeur = humeurs.most_common(1)[0][0] if humeurs else None

    return {
        "total_meetings": len(meetings),
        "total_recordings": len(recordings),
        "categories": categories.most_common(),
        "top_categorie": top_categorie,
        "top_humeur": top_humeur,
    }


def _has_taken_place(date, resume):
    """
    Une réunion visio programmée dans le futur n'a pas encore eu lieu :
    on ne l'affiche nulle part au dashboard tant que ce n'est pas le cas.
    """
    return bool(resume) or not date or date <= datetime.now()


def _merged_items(meetings, recordings):
    items = []

    for type_, rows in (("visio", meetings), ("dicta", recordings)):
        for id_, titre, date, theme, categorie, humeur, resume, actions in rows:

            if not _has_taken_place(date, resume):
                continue

            items.append({
                "type": type_,
                "id": id_,
                "titre": titre,
                "date": date,
                "theme": theme,
                "categorie": categorie,
                "humeur": humeur,
                "resume": resume,
                "actions": actions,
            })

    items.sort(key=lambda item: item["date"], reverse=True)

    return items


def _parse_date_filter(value):
    if not value:
        return None

    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _filter_items(
    items,
    type_filter=None,
    categorie_filter=None,
    periode_filter=None,
    date_debut_filter=None,
    date_fin_filter=None
):
    """
    Filtre la liste des réunions et dictaphones selon :
    - le type : visio ou dicta
    - la catégorie
    - la période : 7j ou 30j
    """

    filtered_items = items

    # Filtre par type
    if type_filter in ("visio", "dicta"):
        filtered_items = [
            item for item in filtered_items
            if item["type"] == type_filter
        ]

    # Filtre par catégorie
    if categorie_filter:
        filtered_items = [
            item for item in filtered_items
            if item["categorie"] == categorie_filter
        ]

    # Filtre par période
    if periode_filter in ("7j", "30j"):

        jours = 7 if periode_filter == "7j" else 30

        date_limite = datetime.now() - timedelta(days=jours)

        filtered_items = [
            item for item in filtered_items
            if item["date"] and item["date"] >= date_limite
        ]

    date_debut = _parse_date_filter(date_debut_filter)
    date_fin = _parse_date_filter(date_fin_filter)

    if date_debut or date_fin:
        filtered_items = [
            item for item in filtered_items
            if item["date"]
            and (not date_debut or item["date"].date() >= date_debut)
            and (not date_fin or item["date"].date() <= date_fin)
        ]

    return filtered_items


@dashboard_bp.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if not check_consent(session['user_id']):
        return render_template("consent.html")

    meetings = [
        m for m in get_user_meetings(session['user_id'])
        if _has_taken_place(m[2], m[6])
    ]

    recordings = get_user_recordings(session['user_id'])
    user = get_user(session['user_id'])

    # Fusion des réunions visio et dictaphones
    items = _merged_items(meetings, recordings)

    # Récupération des filtres présents dans l'URL
    type_filter = request.args.get("type")
    categorie_filter = request.args.get("categorie")
    periode_filter = request.args.get("periode")
    date_debut_filter = request.args.get("date_debut")
    date_fin_filter = request.args.get("date_fin")

    # Application des filtres
    filtered_items = _filter_items(
        items,
        type_filter,
        categorie_filter,
        periode_filter,
        date_debut_filter,
        date_fin_filter
    )

    # Les statistiques restent calculées sur toutes les données
    stats = _stats(meetings, recordings)

    return render_template(
        "dashboard.html",
        items=filtered_items,
        stats=stats,
        user=user,
        active_nav='dashboard',
        type_filter=type_filter,
        categorie_filter=categorie_filter,
        periode_filter=periode_filter,
        date_debut_filter=date_debut_filter,
        date_fin_filter=date_fin_filter
    )


@dashboard_bp.route("/renommer", methods=["POST"])
def renommer():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    table = request.form.get('table')
    row_id = request.form.get('id')
    titre = request.form.get('titre', '').strip()

    if table in TABLES_RENOMMABLES and row_id and titre:
        rename_item(
            session['user_id'],
            table,
            row_id,
            titre
        )

    return redirect(url_for('dashboard.dashboard'))


@dashboard_bp.route("/accept_consent", methods=["POST"])
def accept_consent():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    record_consent(session['user_id'])

    return redirect(url_for('dashboard.dashboard'))
