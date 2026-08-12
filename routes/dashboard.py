"""
Lot 4 : Données & restitution
Tableau de bord, filtres, suppression de compte.
"""

from collections import Counter
from flask import Blueprint, session, redirect, url_for, render_template
from utils.database import check_consent, record_consent, get_user_meetings, get_user_recordings, get_user

dashboard_bp = Blueprint("dashboard", __name__)


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


def _merged_items(meetings, recordings):
    items = []
    for type_, rows in (("visio", meetings), ("dicta", recordings)):
        for id_, titre, date, theme, categorie, humeur, resume, actions in rows:
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


@dashboard_bp.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if not check_consent(session['user_id']):
        return render_template("consent.html")

    meetings = get_user_meetings(session['user_id'])
    recordings = get_user_recordings(session['user_id'])
    user = get_user(session['user_id'])

    return render_template(
        "dashboard.html",
        items=_merged_items(meetings, recordings),
        stats=_stats(meetings, recordings),
        user=user,
        active_nav='dashboard'
    )


@dashboard_bp.route("/accept_consent", methods=["POST"])
def accept_consent():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    record_consent(session['user_id'])
    return redirect(url_for('dashboard.dashboard'))