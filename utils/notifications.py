import logging
import smtplib
from email.message import EmailMessage
from datetime import datetime
from config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD

logger = logging.getLogger(__name__)


def _format_date(date_iso):
    try:
        dt = datetime.fromisoformat(date_iso.replace('Z', '+00:00'))
        return dt.strftime("%d/%m/%Y à %Hh%M")
    except (ValueError, AttributeError):
        return date_iso


def _send_email(to, subject, html):
    message = EmailMessage()
    message["From"] = f"Scribe <{GMAIL_ADDRESS}>"
    message["To"] = to
    message["Subject"] = subject
    message.set_content("Ce message nécessite un client email compatible HTML.")
    message.add_alternative(html, subtype="html")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        smtp.send_message(message)


def notify_recording(participant_emails, titre, date_iso, organisateur_nom):
    """Un email par destinataire (pas d'envoi groupé) pour ne pas exposer la liste des participants entre eux."""
    if not participant_emails:
        return

    date_str = _format_date(date_iso)

    for email in participant_emails:
        try:
            _send_email(
                email,
                f"Scribe va enregistrer la réunion « {titre} »",
                f"""
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
            )
        except Exception:
            logger.exception("Échec de l'envoi de la notification d'enregistrement à %s", email)
