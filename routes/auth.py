"""
Lot 1 : Identité & agenda
OAuth Google, connexion, gestion des utilisateurs.
"""
import json
import os
from flask import Blueprint, request, session, redirect, url_for, render_template
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from utils.database import get_or_create_user, get_user

auth_bp = Blueprint("auth", __name__)

# En mémoire process : nécessite un seul worker gunicorn (voir Procfile), sinon
# le worker qui reçoit /callback peut ne pas être celui qui a créé le flow.
flow_store = {}

SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]


def _build_flow(redirect_uri):
    credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if credentials_json:
        return Flow.from_client_config(
            json.loads(credentials_json),
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )
    return Flow.from_client_secrets_file(
        'credentials.json',
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )


@auth_bp.route("/login")
def login():
    flow = _build_flow(url_for('auth.callback', _external=True))
    auth_url, state = flow.authorization_url(prompt='select_account')
    flow_store[state] = flow
    return redirect(auth_url)



@auth_bp.route("/callback")
def callback():
    state = request.args.get('state')
    flow = flow_store[state]
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials

    service_user = build('oauth2', 'v2', credentials=creds)
    user_info = service_user.userinfo().get().execute()

    id_user = get_or_create_user(user_info['email'], user_info['name'])

    session['user_id'] = id_user
    session['creds'] = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }

    return redirect(url_for('dashboard.dashboard'))



@auth_bp.route("/profil")
def profil():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    return render_template("profil.html", user=get_user(session['user_id']))


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))


@auth_bp.route("/conditions")
def conditions():
    with open("dpa.txt", "r", encoding="utf-8") as f:
        contenu = f.read()
    return f"<pre>{contenu}</pre>"