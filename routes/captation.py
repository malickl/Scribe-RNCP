"""
Lot 2 : Captation
Regroupe les deux modes de captation audio : visio (bot Recall) et dictaphone (upload micro).
Ne pas séparer dictaphone dans un autre fichier : les deux modes de captation vivent ici ensemble.
"""

from flask import Blueprint, request, session, redirect, url_for, jsonify
from utils.database import insert_dictaphone
from routes.pipeline import run_pipeline
import threading
from flask import render_template

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

@captation_bp.route("/dictaphone", methods=["POST"])
def dictaphone():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    audio = request.files["audio"]
    filename = f"dictaphone_{session['user_id']}.wav"
    audio.save(filename)

    id_dictaphone = insert_dictaphone(session['user_id'], "Enregistrement")

    threading.Thread(
        target=run_pipeline,
        args=(filename, "dictaphones", id_dictaphone),
        daemon=True
    ).start()

    return jsonify({"message": "Traitement en cours", "id": id_dictaphone}), 200



@captation_bp.route("/dictaphone", methods=["GET"])
def dictaphone_page():
    return render_template("dictaphone.html")

from routes.pipeline import run_pipeline
from utils.recall import get_audio
from utils.database import get_reunion_by_bot_id
import threading

@captation_bp.route("/webhook/recall", methods=["POST"])
def webhook_recall():
    data = request.json

    if data.get("event") != "bot.done":
        return '', 200

    bot_id = data["data"]["bot"]["id"]

    id_reunion = get_reunion_by_bot_id(bot_id)
    if id_reunion is None:
        return '', 200

    filename = get_audio(bot_id)

    threading.Thread(
        target=run_pipeline,
        args=(filename, "reunions", id_reunion),
        daemon=True
    ).start()

    return '', 200