"""
Lot 2 : Captation
Regroupe les deux modes de captation audio : visio (bot Recall) et dictaphone (upload micro).
Ne pas séparer dictaphone dans un autre fichier : les deux modes de captation vivent ici ensemble.
"""

from flask import Blueprint, request, session, redirect, url_for, jsonify, render_template
from utils.database import insert_dictaphone
from utils.database import get_user
from utils.database import get_all_reunion_keys
from utils.database import get_user_reunion_ids
from utils.database import add_reunion_participant
from routes.pipeline import run_pipeline
from googleapiclient.discovery import build
import threading
import os
import uuid
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from datetime import datetime, timezone
from utils.recall import get_audio
from utils.database import get_reunion_by_bot_id
from utils.database import insert_reunion
from utils.recall import send_bot

JOURS_FR = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
MOIS_FR = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]


def _jour_label(dt):
    aujourdhui = datetime.now(dt.tzinfo).date()
    diff = (dt.date() - aujourdhui).days
    if diff == 0:
        return "Aujourd'hui"
    if diff == 1:
        return "Demain"
    return f"{JOURS_FR[dt.weekday()].capitalize()} {dt.day} {MOIS_FR[dt.month - 1]}"


def _group_by_day(reunions_list):
    groups = []
    for r in reunions_list:
        label = r["jour_label"]
        if not groups or groups[-1]["label"] != label:
            groups.append({"label": label, "reunions": []})
        groups[-1]["reunions"].append(r)
    return groups


def _event_key(titre, date_iso):
    dt = datetime.fromisoformat(date_iso.replace('Z', '+00:00'))
    return (titre, dt.strftime('%Y-%m-%dT%H:%M:%S'))


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

    all_reunion_keys = get_all_reunion_keys()
    mes_reunion_ids = get_user_reunion_ids(session['user_id'])

    reunions_list = []
    for event in events.get('items', []):
        lien = event.get('hangoutLink')
        date_iso = event['start'].get('dateTime')
        if not lien or not date_iso:
            continue
        dt = datetime.fromisoformat(date_iso.replace('Z', '+00:00'))
        titre = event.get('summary', 'Sans titre')

        id_reunion = all_reunion_keys.get(_event_key(titre, date_iso))
        if id_reunion is None:
            statut = "aucun_bot"
        elif id_reunion in mes_reunion_ids:
            statut = "deja_recu"
        else:
            statut = "bot_dun_autre"

        reunions_list.append({
            "titre": titre,
            "date": date_iso,
            "heure": dt.strftime("%Hh%M"),
            "jour_label": _jour_label(dt),
            "participants": [p['email'] for p in event.get('attendees', [])],
            "lien": lien,
            "statut": statut,
            "id_reunion": id_reunion
        })

    return render_template(
        "reunions.html",
        jours=_group_by_day(reunions_list),
        user=get_user(session['user_id']),
        active_nav='reunions'
    )

@captation_bp.route("/dictaphone", methods=["POST"])
def dictaphone():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    audio = request.files["audio"]
    extension = os.path.splitext(audio.filename)[1] or ".webm"
    filename = f"dictaphone_{session['user_id']}_{uuid.uuid4().hex}{extension}"
    audio.save(filename)

    titre = request.form.get("titre", "").strip() or "Enregistrement dictaphone"
    id_dictaphone = insert_dictaphone(session['user_id'], titre)

    threading.Thread(
        target=run_pipeline,
        args=(filename, "dictaphones", id_dictaphone),
        daemon=True
    ).start()

    return jsonify({"message": "Traitement en cours", "id": id_dictaphone}), 200



@captation_bp.route("/dictaphone", methods=["GET"])
def dictaphone_page():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    return render_template("dictaphone.html", user=get_user(session['user_id']), active_nav='dictaphone')



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

    if _event_key(title, date) in get_all_reunion_keys():
        # Un bot a déjà été envoyé pour cette réunion (par n'importe qui)
        # entre le chargement de la page et ce clic : on ne double pas.
        return redirect(url_for('captation.reunions'))

    try:
        bot_id = send_bot(link)
    except RuntimeError:
        return redirect(url_for('captation.reunions'))

    insert_reunion(session['user_id'], title, date, bot_id)

    return redirect(url_for('captation.reunions'))


@captation_bp.route("/recevoir_compte_rendu", methods=["POST"])
def recevoir_compte_rendu():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    id_reunion = request.form.get('id_reunion')
    if id_reunion:
        add_reunion_participant(id_reunion, session['user_id'])

    return redirect(url_for('captation.reunions'))