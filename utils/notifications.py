"""
Emails de notification (pas le contenu du compte-rendu, juste des avis).
"""

import logging
import resend
from datetime import datetime
from config import RESEND_FROM

logger = logging.getLogger(__name__)


def _format_date(date_iso):
    try:
        dt = datetime.fromisoformat(date_iso.replace('Z', '+00:00'))
        return dt.strftime("%d/%m/%Y à %Hh%M")
    except (ValueError, AttributeError):
        return date_iso


def notify_recording(participant_emails, titre, date_iso, organisateur_nom):
    """Prévient chaque participant, dès l'affectation du bot, que Scribe va
    rejoindre et enregistrer la réunion. Envoyée un email par destinataire
    (pas un envoi groupé) pour ne pas exposer la liste des participants les
    uns aux autres. Une erreur d'envoi est loguée et n'empêche jamais
    l'affectation du bot."""
    if not participant_emails:
        return

    date_str = _format_date(date_iso)

    for email in participant_emails:
        try:
            resend.Emails.send({
                "from": RESEND_FROM,
                "to": [email],
                "subject": f"Scribe va enregistrer la réunion « {titre} »",
                "html": f"""
                    <p>Bonjour,</p>
                    <p>{organisateur_nom} a programmé <strong>Scribe</strong>
                    pour rejoindre et enregistrer la réunion
                    « {titre} », prévue le {date_str}.</p>
                    <p>Scribe enregistre l'audio de la réunion afin d'en
                    produire une transcription et un compte-rendu.
                    Si vous ne souhaitez pas être enregistré·e,
                    merci de le signaler à l'organisateur avant le début
                    de la réunion.</p>
                    <p>— Scribe</p>
                """
            })
        except Exception:
            logger.exception("Échec de l'envoi de la notification d'enregistrement à %s", email)
