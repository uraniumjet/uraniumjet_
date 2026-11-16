"""Sends the contact-form message to the company inbox.

Backends (set MAIL_BACKEND):
  resend   HTTPS API call to Resend. Works on any host, including ones that block SMTP.
  smtp     Plain SMTP, for example Gmail with an app password.
  console  Prints the message to the log. For local development only.
"""
from __future__ import annotations

import logging
import smtplib
import ssl
from email.message import EmailMessage

import requests

log = logging.getLogger("uraniumjet.mail")


def is_configured(cfg) -> bool:
    backend = cfg.get("MAIL_BACKEND", "")
    if backend == "console":
        return True
    if backend == "resend":
        return bool(cfg.get("RESEND_API_KEY") and cfg.get("MAIL_FROM") and cfg.get("MAIL_TO"))
    if backend == "smtp":
        return bool(cfg.get("SMTP_HOST") and cfg.get("MAIL_FROM") and cfg.get("MAIL_TO"))
    return False


def _clean_line(value: str) -> str:
    return " ".join(value.split())


def build_text(name: str, email: str, phone: str, topic_label: str, message: str) -> str:
    lines = [
        f"Name: {name}",
        f"Email: {email}",
        f"Phone: {phone or 'not given'}",
        f"Interested in: {topic_label}",
        "",
        message,
    ]
    return "\n".join(lines)


def send_contact(cfg, *, name: str, email: str, phone: str, topic_label: str, message: str) -> tuple[bool, str]:
    """Returns (ok, error_message). Never raises."""
    subject = f"Website enquiry from {_clean_line(name)[:60]}"
    body = build_text(name, email, phone, topic_label, message)
    backend = cfg.get("MAIL_BACKEND", "")
    try:
        if backend == "console":
            log.warning("CONTACT MESSAGE (console backend)\nSubject: %s\nReply-To: %s\n%s", subject, email, body)
            return True, ""
        if backend == "resend":
            resp = requests.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {cfg['RESEND_API_KEY']}"},
                json={
                    "from": cfg["MAIL_FROM"],
                    "to": [cfg["MAIL_TO"]],
                    "reply_to": email,
                    "subject": subject,
                    "text": body,
                },
                timeout=10,
            )
            if resp.status_code >= 300:
                log.error("Resend rejected the message: %s %s", resp.status_code, resp.text[:300])
                return False, "mail provider rejected the message"
            return True, ""
        if backend == "smtp":
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = cfg["MAIL_FROM"]
            msg["To"] = cfg["MAIL_TO"]
            msg["Reply-To"] = email
            msg.set_content(body)
            host, port = cfg["SMTP_HOST"], int(cfg.get("SMTP_PORT", 587))
            ctx = ssl.create_default_context()
            if port == 465:
                with smtplib.SMTP_SSL(host, port, context=ctx, timeout=15) as s:
                    _login(s, cfg)
                    s.send_message(msg)
            else:
                with smtplib.SMTP(host, port, timeout=15) as s:
                    s.starttls(context=ctx)
                    _login(s, cfg)
                    s.send_message(msg)
            return True, ""
        return False, "mail is not configured"
    except Exception:  # network errors, auth errors, bad header values
        log.exception("Sending the contact message failed")
        return False, "could not reach the mail service"


def _login(server, cfg) -> None:
    if cfg.get("SMTP_USER"):
        server.login(cfg["SMTP_USER"], cfg.get("SMTP_PASSWORD", ""))
