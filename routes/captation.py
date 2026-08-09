"""
Lot 2 : Captation
Regroupe les deux modes de captation audio : visio (bot Recall) et dictaphone (upload micro).
Ne pas séparer dictaphone dans un autre fichier : les deux modes de captation vivent ici ensemble.
"""

from flask import Blueprint, request, session, redirect, url_for, jsonify
from utils.database import insert_dictaphone
from routes.pipeline import run_pipeline
from googleapiclient.discovery import build
import threading
import os
import uuid
from flask import render_template
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from datetime import datetime, timezone
from utils.recall import get_audio
from utils.database import get_reunion_by_bot_id
from utils.database import insert_reunion
from utils.recall import send_bot

captation_bp = Blueprint("captation", __name__)

@captation_bp.route("/reunions")
def reunions():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    creds = Credentials(**session['creds'])
    if creds.expired and creds.refresh_token:
        creds.refresh(GoogleRequest())
        session['creds']['token'] = creds.token

    service = build('calendar', 'v3', credentials=creds)

    now = datetime.now(timezone.utc).isoformat()

    events = service.events().list(
        calendarId='primary',
        maxResults=20,
        singleEvents=True,
        orderBy='startTime',
        timeMin=now
    ).execute()

    reunions_list = []
    for event in events.get('items', []):
        lien = event.get('hangoutLink')
        if not lien:
            continue
        reunions_list.append({
            "titre": event.get('summary', 'Sans titre'),
            "date": event['start'].get('dateTime'),
            "participants": [p['email'] for p in event.get('attendees', [])],
            "lien": lien
        })

    return render_template("reunions.html", reunions=reunions_list)

@captation_bp.route("/dictaphone", methods=["POST"])
def dictaphone():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    audio = request.files["audio"]
    extension = os.path.splitext(audio.filename)[1] or ".webm"
    filename = f"dictaphone_{session['user_id']}_{uuid.uuid4().hex}{extension}"
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

@captation_bp.route("/envoyer_bot", methods=["POST"])
def envoyer_bot():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    link = request.form.get('link')
    title = request.form.get('title')
    date = request.form.get('date')

    try:
        bot_id = send_bot(link)
    except RuntimeError:
        return redirect(url_for('captation.reunions'))

    insert_reunion(session['user_id'], title, date, bot_id)

    return redirect(url_for('captation.reunions'))