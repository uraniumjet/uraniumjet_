import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import mailer  # noqa: E402
from app import create_app  # noqa: E402

PAGES = ["/", "/products", "/products/hostel-meals", "/services", "/how-we-work", "/team", "/contact"]


@pytest.fixture
def app():
    return create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret",
        "MAIL_BACKEND": "console",
        "MIN_FILL_SECONDS": 0,
        "SESSION_COOKIE_SECURE": False,
        "WHATSAPP_NUMBER": "2349034097508",
    })


@pytest.fixture
def client(app):
    return app.test_client()


def token_for(client):
    html = client.get("/contact").get_data(as_text=True)
    return re.search(r'name="csrf" value="([^"]+)"', html).group(1)


def valid_form(token, **over):
    data = {
        "csrf": token,
        "name": "Aisha Bello",
        "email": "aisha@example.com",
        "phone": "+234 803 000 0000",
        "topic": "hostel-meals",
        "message": "We run a hostel with 400 students and want to try the system.",
        "website": "",
    }
    data.update(over)
    return data


@pytest.fixture
def sent(monkeypatch):
    calls = []

    def fake(cfg, **kw):
        calls.append(kw)
        return True, ""

    monkeypatch.setattr(mailer, "send_contact", fake)
    return calls


# ------------------------------------------------------------------ pages
@pytest.mark.parametrize("path", PAGES)
def test_pages_load(client, path):
    r = client.get(path)
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert "<h1" in html
    assert 'rel="canonical"' in html


@pytest.mark.parametrize("path", PAGES)
def test_whatsapp_button_on_every_page(client, path):
    html = client.get(path).get_data(as_text=True)
    assert "https://wa.me/2349034097508?text=" in html
    assert 'class="wa-float"' in html


def test_home_links_to_live_demo(client):
    html = client.get("/").get_data(as_text=True)
    assert 'href="https://hostel-meals-demo.onrender.com"' in html


def test_nav_has_required_sections(client):
    html = client.get("/").get_data(as_text=True)
    for label in ["Products", "Services", "How we work", "Team", "Contact"]:
        assert f">{label}</a>" in html


def test_no_inline_style_or_script_so_csp_holds(client):
    for path in PAGES:
        html = client.get(path).get_data(as_text=True)
        assert " style=" not in html, path
        assert re.search(r"<script(?![^>]*(src=|application/ld\+json))", html) is None, path
        assert re.search(r"\son[a-z]+=", html) is None, path


def test_security_headers(client):
    r = client.get("/")
    assert "default-src 'self'" in r.headers["Content-Security-Policy"]
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"


def test_404_page(client):
    r = client.get("/nope")
    assert r.status_code == 404
    assert "Page not found" in r.get_data(as_text=True)


def test_healthz_robots_sitemap(client):
    assert client.get("/healthz").json == {"status": "ok"}
    assert "Sitemap:" in client.get("/robots.txt").get_data(as_text=True)
    xml = client.get("/sitemap.xml").get_data(as_text=True)
    for path in PAGES[1:]:
        assert path in xml


def test_static_assets_exist(client):
    for p in ["/static/css/site.css", "/static/js/site.js", "/static/img/yusuf.jpg",
              "/static/img/ahmad.jpg", "/static/img/og.png", "/static/img/favicon.svg"]:
        assert client.get(p).status_code == 200, p


def test_services_anchors_match_home_links(client):
    home = client.get("/").get_data(as_text=True)
    services = client.get("/services").get_data(as_text=True)
    for anchor in re.findall(r'/services#([a-z-]+)', home):
        assert f'id="{anchor}"' in services


# ---------------------------------------------------------------- contact
def test_contact_success_sends_mail_and_redirects(client, sent):
    token = token_for(client)
    r = client.post("/contact", data=valid_form(token))
    assert r.status_code == 303 and r.headers["Location"].endswith("/contact/sent")
    assert len(sent) == 1
    assert sent[0]["email"] == "aisha@example.com"
    assert sent[0]["topic_label"] == "The Hostel Meals system"
    page = client.get("/contact/sent")
    assert page.status_code == 200 and "Message sent" in page.get_data(as_text=True)
    # the thank-you page only shows once
    assert client.get("/contact/sent").status_code == 302


def test_sent_page_needs_a_submission(client):
    assert client.get("/contact/sent").status_code == 302


def test_validation_errors_keep_input(client, sent):
    token = token_for(client)
    r = client.post("/contact", data=valid_form(token, email="not-an-email", message="short", name="A"))
    html = r.get_data(as_text=True)
    assert r.status_code == 422
    assert not sent
    assert "Enter an email address" in html
    assert "Write a message between 10 and 3000" in html
    assert 'value="A"' in html  # input preserved
    assert 'aria-invalid="true"' in html


def test_invalid_topic_and_phone(client, sent):
    token = token_for(client)
    r = client.post("/contact", data=valid_form(token, topic="hack", phone="abc"))
    html = r.get_data(as_text=True)
    assert r.status_code == 422 and not sent
    assert "Choose what you need help with" in html and "Use digits only" in html


def test_missing_csrf_rejected(client, sent):
    client.get("/contact")
    r = client.post("/contact", data=valid_form("wrong"))
    assert r.status_code == 400 and not sent
    assert "expired" in r.get_data(as_text=True)


def test_post_without_visiting_form_rejected(client, sent):
    r = client.post("/contact", data=valid_form("anything"))
    assert r.status_code == 400 and not sent


def test_honeypot_pretends_success_but_sends_nothing(client, sent):
    token = token_for(client)
    r = client.post("/contact", data=valid_form(token, website="http://spam.example"))
    assert r.status_code == 303 and not sent


def test_too_fast_submission_rejected(app, sent):
    app.config["MIN_FILL_SECONDS"] = 30
    c = app.test_client()
    token = token_for(c)
    r = c.post("/contact", data=valid_form(token))
    assert r.status_code == 400 and not sent


def test_rate_limit(client, sent):
    for _ in range(5):
        token = token_for(client)
        assert client.post("/contact", data=valid_form(token)).status_code == 303
    token = token_for(client)
    r = client.post("/contact", data=valid_form(token))
    assert r.status_code == 429
    assert len(sent) == 5


def test_mail_failure_shows_message_and_keeps_input(client, monkeypatch):
    monkeypatch.setattr(mailer, "send_contact", lambda cfg, **kw: (False, "boom"))
    token = token_for(client)
    r = client.post("/contact", data=valid_form(token))
    html = r.get_data(as_text=True)
    assert r.status_code == 502
    assert "could not send your message" in html
    assert "Aisha Bello" in html


def test_unconfigured_mail_returns_503_not_silent_success(app, sent):
    app.config["MAIL_BACKEND"] = "resend"
    app.config["RESEND_API_KEY"] = ""
    c = app.test_client()
    token = token_for(c)
    r = c.post("/contact", data=valid_form(token))
    assert r.status_code == 503 and not sent
    assert "temporarily unavailable" in r.get_data(as_text=True)


def test_topic_preselected_from_query(client):
    html = client.get("/contact?topic=it-support").get_data(as_text=True)
    assert re.search(r'<option value="it-support" selected>', html)


def test_missing_secret_key_refuses_to_start(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("FLASK_DEBUG", raising=False)
    with pytest.raises(RuntimeError):
        create_app()


# ----------------------------------------------------------------- mailer
def test_resend_payload(monkeypatch):
    captured = {}

    class Resp:
        status_code = 200
        text = "{}"

    def fake_post(url, headers, json, timeout):
        captured.update(url=url, headers=headers, json=json)
        return Resp()

    monkeypatch.setattr(mailer.requests, "post", fake_post)
    cfg = {"MAIL_BACKEND": "resend", "RESEND_API_KEY": "k", "MAIL_FROM": "Site <a@b.com>", "MAIL_TO": "me@x.com"}
    ok, _ = mailer.send_contact(cfg, name="Ann\nBcc: evil@x.com", email="a@x.com", phone="", topic_label="Other", message="hello there friend")
    assert ok
    assert captured["json"]["reply_to"] == "a@x.com"
    assert captured["json"]["to"] == ["me@x.com"]
    assert "\n" not in captured["json"]["subject"]
    assert captured["headers"]["Authorization"] == "Bearer k"


def test_resend_error_status_is_failure(monkeypatch):
    class Resp:
        status_code = 403
        text = "forbidden"

    monkeypatch.setattr(mailer.requests, "post", lambda *a, **k: Resp())
    cfg = {"MAIL_BACKEND": "resend", "RESEND_API_KEY": "k", "MAIL_FROM": "a@b.com", "MAIL_TO": "me@x.com"}
    ok, _ = mailer.send_contact(cfg, name="Ann", email="a@x.com", phone="", topic_label="Other", message="hello there friend")
    assert not ok


def test_resend_network_error_does_not_raise(monkeypatch):
    def boom(*a, **k):
        raise mailer.requests.ConnectionError("down")

    monkeypatch.setattr(mailer.requests, "post", boom)
    cfg = {"MAIL_BACKEND": "resend", "RESEND_API_KEY": "k", "MAIL_FROM": "a@b.com", "MAIL_TO": "me@x.com"}
    ok, _ = mailer.send_contact(cfg, name="Ann", email="a@x.com", phone="", topic_label="Other", message="hello there friend")
    assert not ok
