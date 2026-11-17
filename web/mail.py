"""Send the enquiry notification. The enquiry is already saved before this runs, so a failure here loses nothing."""
import json
import logging
import urllib.error
import urllib.request

from django.conf import settings

log = logging.getLogger(__name__)


def _clean(text):
    return " ".join(str(text).split())


def notify(enquiry):
    """Return True if the notification email was handed to the provider."""
    subject = _clean(f"New enquiry from {enquiry.name}: {enquiry.get_topic_display()}")
    body = (
        f"Name: {_clean(enquiry.name)}\n"
        f"Email: {_clean(enquiry.email)}\n"
        f"Phone: {_clean(enquiry.phone) or 'not given'}\n"
        f"Topic: {enquiry.get_topic_display()}\n\n"
        f"{enquiry.message}\n"
    )
    if settings.MAIL_BACKEND == "console":
        print(f"\n--- Enquiry (console mail backend) ---\nTo: {settings.MAIL_TO}\nSubject: {subject}\n\n{body}---", flush=True)
        return True
    if settings.MAIL_BACKEND == "resend":
        if not (settings.RESEND_API_KEY and settings.MAIL_FROM):
            log.error("Resend selected but RESEND_API_KEY or MAIL_FROM is missing.")
            return False
        payload = json.dumps({
            "from": settings.MAIL_FROM,
            "to": [settings.MAIL_TO],
            "reply_to": _clean(enquiry.email),
            "subject": subject,
            "text": body,
        }).encode()
        req = urllib.request.Request(
            "https://api.resend.com/emails",
            data=payload,
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
                "User-Agent": "uranium-jet-digital-solution-site/1.0",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                return 200 <= resp.status < 300
        except (urllib.error.URLError, TimeoutError) as exc:
            log.error("Resend request failed: %s", exc)
            return False
    log.error("Unknown MAIL_BACKEND %r", settings.MAIL_BACKEND)
    return False
