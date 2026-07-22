"""
Lot 4 : Données & restitution
Tableau de bord, filtres, suppression de compte.
"""

from flask import Blueprint, session, redirect, url_for, render_template
from utils.database import check_consent

dashboard_bp = Blueprint("dashboard", __name__)



dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if not check_consent(session['user_id']):
        return render_template("consentement.html")

    #TODO: afficher le vrai contenu du dashboard (dépend de KAN-27/28)
    return "Dashboard normal ici"
