"""Uranium Jet Digital Solution company website (Flask)."""
from __future__ import annotations

import hmac
import os
import re
import secrets
import time
from collections import defaultdict, deque
from copy import deepcopy
from datetime import datetime, timezone
from urllib.parse import quote

from flask import Flask, Response, redirect, render_template, request, session, url_for
from werkzeug.middleware.proxy_fix import ProxyFix

import content
import mailer

EMAIL_RE = re.compile(r"^[^@\s<>,;:\"']+@[^@\s<>,;:\"']+\.[^@\s<>,;:\"']{2,}$")
PHONE_RE = re.compile(r"^[0-9+()\-\s]{6,30}$")
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


class RateLimiter:
    """Small in-memory limiter. Each server process keeps its own counts."""

    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window = window_seconds
        self.hits: dict[str, deque] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        if len(self.hits) > 5000:
            self.hits = defaultdict(deque, {k: v for k, v in self.hits.items() if v and now - v[-1] < self.window})
        q = self.hits[key]
        while q and now - q[0] > self.window:
            q.popleft()
        if len(q) >= self.limit:
            return False
        q.append(now)
        return True


def _env_flag(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(int(default))).strip().lower() in {"1", "true", "yes", "on"}


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    debug = _env_flag("FLASK_DEBUG")

    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", ""),
        SITE_URL=os.getenv("SITE_URL", "").rstrip("/"),
        WHATSAPP_NUMBER=os.getenv("WHATSAPP_NUMBER", content.SITE["whatsapp"]),
        MAIL_BACKEND=os.getenv("MAIL_BACKEND", "console" if debug else "resend"),
        MAIL_FROM=os.getenv("MAIL_FROM", ""),
        MAIL_TO=os.getenv("MAIL_TO", content.SITE["email"]),
        RESEND_API_KEY=os.getenv("RESEND_API_KEY", ""),
        SMTP_HOST=os.getenv("SMTP_HOST", ""),
        SMTP_PORT=os.getenv("SMTP_PORT", "587"),
        SMTP_USER=os.getenv("SMTP_USER", ""),
        SMTP_PASSWORD=os.getenv("SMTP_PASSWORD", ""),
        CONTACT_LIMIT=5,  # messages per IP address...
        CONTACT_WINDOW=600,  # ...per this many seconds
        MIN_FILL_SECONDS=2,  # a human cannot fill the form faster than this
        FORM_MAX_AGE=6 * 3600,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=not debug,
        SEND_FILE_MAX_AGE_DEFAULT=60 * 60 * 24 * 30,
        MAX_CONTENT_LENGTH=64 * 1024,
        TRUST_PROXY=_env_flag("TRUST_PROXY"),
        DEBUG=debug,
    )
    if test_config:
        app.config.update(test_config)

    if not app.config["SECRET_KEY"]:
        if debug or app.config.get("TESTING"):
            app.config["SECRET_KEY"] = secrets.token_hex(32)
        else:
            raise RuntimeError("SECRET_KEY is not set. Set it as an environment variable before starting the site.")

    if app.config["TRUST_PROXY"]:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    limiter = RateLimiter(app.config["CONTACT_LIMIT"], app.config["CONTACT_WINDOW"])
    topics = dict(content.CONTACT_TOPICS)

    # ------------------------------------------------------------------ helpers
    def whatsapp_url(text: str | None = None) -> str:
        message = text or content.SITE["whatsapp_text"]
        return f"https://wa.me/{app.config['WHATSAPP_NUMBER']}?text={quote(message)}"

    def asset(filename: str) -> str:
        path = os.path.join(app.static_folder, filename)
        try:
            version = int(os.path.getmtime(path))
        except OSError:
            version = 0
        return url_for("static", filename=filename, v=version)

    def absolute(endpoint: str, **values) -> str:
        base = app.config["SITE_URL"] or request.url_root.rstrip("/")
        return base + url_for(endpoint, **values)

    @app.context_processor
    def inject_globals():
        site = deepcopy(content.SITE)
        site["whatsapp"] = app.config["WHATSAPP_NUMBER"]
        return {
            "site": site,
            "nav": content.NAV,
            "whatsapp_url": whatsapp_url,
            "asset": asset,
            "absolute": absolute,
            "year": datetime.now(timezone.utc).year,
            "current_endpoint": request.endpoint,
        }

    @app.after_request
    def security_headers(resp: Response) -> Response:
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        resp.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; "
            "base-uri 'self'; form-action 'self'; frame-ancestors 'none'; object-src 'none'",
        )
        if request.is_secure:
            resp.headers.setdefault("Strict-Transport-Security", "max-age=31536000")
        if request.endpoint == "contact" or request.endpoint == "contact_sent":
            resp.headers["Cache-Control"] = "no-store"
        return resp

    # ------------------------------------------------------------------- pages
    @app.get("/")
    def home():
        return render_template(
            "home.html",
            groups=content.SERVICE_GROUPS,
            hostel=content.PRODUCT_HOSTEL,
            planned=content.PRODUCTS_PLANNED,
            process=content.PROCESS,
            team=content.TEAM,
        )

    @app.get("/products")
    def products():
        return render_template("products.html", hostel=content.PRODUCT_HOSTEL, planned=content.PRODUCTS_PLANNED)

    @app.get("/products/hostel-meals")
    def product_hostel():
        return render_template("product_hostel.html", hostel=content.PRODUCT_HOSTEL)

    @app.get("/services")
    def services():
        return render_template("services.html", groups=content.SERVICE_GROUPS)

    @app.get("/how-we-work")
    def how_we_work():
        return render_template("how_we_work.html", process=content.PROCESS)

    @app.get("/team")
    def team():
        return render_template("team.html", team=content.TEAM, values=content.VALUES)

    # ----------------------------------------------------------------- contact
    def _new_form_state() -> str:
        token = secrets.token_urlsafe(24)
        session["csrf"] = token
        session["form_ts"] = time.time()
        return token

    def _render_contact(form: dict, errors: dict, token: str, status: int = 200, notice: str = ""):
        return (
            render_template(
                "contact.html",
                form=form,
                errors=errors,
                token=token,
                topics=content.CONTACT_TOPICS,
                notice=notice,
            ),
            status,
        )

    @app.get("/contact")
    def contact():
        topic = request.args.get("topic", "")
        form = {"topic": topic if topic in topics else ""}
        return _render_contact(form, {}, _new_form_state())

    @app.post("/contact")
    def contact_submit():
        raw = request.form
        form = {
            "name": CONTROL_RE.sub("", raw.get("name", "")).strip(),
            "email": raw.get("email", "").strip(),
            "phone": raw.get("phone", "").strip(),
            "topic": raw.get("topic", "").strip(),
            "message": CONTROL_RE.sub("", raw.get("message", "")).strip(),
        }

        # Bots fill the hidden field. Act as if it worked so they learn nothing.
        if raw.get("website", "").strip():
            return redirect(url_for("contact_sent"), 303)

        expected = session.get("csrf", "")
        sent = raw.get("csrf", "")
        filled_at = session.get("form_ts", 0)
        if not expected or not hmac.compare_digest(expected, sent):
            return _render_contact(form, {}, _new_form_state(), 400, "This form expired. Please check your message and send it again.")
        age = time.time() - filled_at
        if age > app.config["FORM_MAX_AGE"]:
            return _render_contact(form, {}, _new_form_state(), 400, "This form expired. Please check your message and send it again.")
        if age < app.config["MIN_FILL_SECONDS"]:
            return _render_contact(form, {}, expected, 400, "That was very quick. Please check your message and press send again.")

        if not limiter.allow(request.remote_addr or "unknown"):
            return _render_contact(
                form, {}, expected, 429,
                "You have sent several messages in a short time. Please wait a few minutes, or message us on WhatsApp.",
            )

        errors = {}
        if not 2 <= len(form["name"]) <= 80:
            errors["name"] = "Enter your name (2 to 80 characters)."
        if len(form["email"]) > 254 or not EMAIL_RE.match(form["email"]):
            errors["email"] = "Enter an email address we can reply to, like name@example.com."
        if form["phone"] and not PHONE_RE.match(form["phone"]):
            errors["phone"] = "Use digits only, with an optional + at the start."
        if form["topic"] not in topics:
            errors["topic"] = "Choose what you need help with."
        if not 10 <= len(form["message"]) <= 3000:
            errors["message"] = "Write a message between 10 and 3000 characters."
        if errors:
            return _render_contact(form, errors, expected, 422)

        if not mailer.is_configured(app.config):
            app.logger.error("Contact form used but mail is not configured (MAIL_BACKEND=%s)", app.config["MAIL_BACKEND"])
            return _render_contact(
                form, {}, expected, 503,
                "Our contact form is temporarily unavailable. Please message us on WhatsApp or email us directly.",
            )

        ok, _ = mailer.send_contact(
            app.config,
            name=form["name"],
            email=form["email"],
            phone=form["phone"],
            topic_label=topics[form["topic"]],
            message=form["message"],
        )
        if not ok:
            return _render_contact(
                form, {}, expected, 502,
                "We could not send your message just now. Nothing was lost on your side: try again, or message us on WhatsApp.",
            )

        session.pop("csrf", None)
        session.pop("form_ts", None)
        session["sent"] = True
        return redirect(url_for("contact_sent"), 303)

    @app.get("/contact/sent")
    def contact_sent():
        if not session.pop("sent", None):
            return redirect(url_for("contact"))
        return render_template("contact_sent.html")

    # --------------------------------------------------------- machine-readable
    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}

    @app.get("/robots.txt")
    def robots():
        body = f"User-agent: *\nAllow: /\nSitemap: {absolute('sitemap')}\n"
        return Response(body, mimetype="text/plain")

    @app.get("/sitemap.xml")
    def sitemap():
        endpoints = ["home", "products", "product_hostel", "services", "how_we_work", "team", "contact"]
        urls = "".join(f"<url><loc>{absolute(e)}</loc></url>" for e in endpoints)
        xml = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>'
        return Response(xml, mimetype="application/xml")

    # ------------------------------------------------------------------ errors
    @app.errorhandler(404)
    def not_found(_e):
        return render_template("error.html", code=404, title="Page not found",
                               message="That page does not exist, or it has moved."), 404

    @app.errorhandler(413)
    def too_large(_e):
        return render_template("error.html", code=413, title="Message too large",
                               message="That request was too large. Please shorten your message."), 413

    @app.errorhandler(500)
    def server_error(_e):
        return render_template("error.html", code=500, title="Something went wrong",
                               message="We have been unable to load this page. Please try again in a moment."), 500

    return app
