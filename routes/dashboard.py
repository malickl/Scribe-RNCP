"""
Lot 4 : Données & restitution
Tableau de bord, filtres, suppression de compte.
"""

from flask import Blueprint, session, redirect, url_for, render_template
from utils.database import check_consent, get_user_meetings, get_user_recordings

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if not check_consent(session['user_id']):
        return render_template("consent.html")

    reunions = get_user_meetings(session['user_id'])
    dictaphones = get_user_recordings(session['user_id'])

    return render_template("dashboard.html", reunions=reunions, dictaphones=dictaphones)