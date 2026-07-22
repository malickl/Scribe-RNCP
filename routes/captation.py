"""
Lot 2 : Captation
Regroupe les deux modes de captation audio : visio (bot Recall) et dictaphone (upload micro).
Ne pas séparer dictaphone dans un autre fichier : les deux modes de captation vivent ici ensemble.
"""

from flask import Blueprint

captation_bp = Blueprint("captation", __name__)

# @captation_bp.route("/reunions")
# def reunions():
#     ...

# @captation_bp.route("/envoyer_bot", methods=["POST"])
# def envoyer_bot():
#     ...

# @captation_bp.route("/webhook/recall", methods=["POST"])
# def webhook_recall():
#     ...

# @captation_bp.route("/dictaphone", methods=["POST"])
# def dictaphone():
#     ...
