"""
Lot 1 : Identité & agenda
OAuth Google, connexion, gestion des utilisateurs.
"""
from flask import Blueprint, redirect, session
from google_auth_oauthlib.flow import Flow

auth_bp = Blueprint("auth", __name__)

flow_store = {}

SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]

@auth_bp.route("/login")
def login():
    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=SCOPES,
        redirect_uri='http://127.0.0.1:5001/callback'
    )
    auth_url, state = flow.authorization_url(prompt='select_account')
    flow_store[state] = flow
    return redirect(auth_url)

# @auth_bp.route("/callback")
# def callback():
#     ...
