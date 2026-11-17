# Uranium Jet Digital Solution: company website

Django 5.2 (Python). Server-rendered pages, hand-written CSS, no JavaScript framework, no build step.
Contact enquiries are saved in the database first, then emailed.

## Run it on your computer

```bash
python3 -m venv .venv
source .venv/bin/activate            # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
export DJANGO_DEBUG=1                # Windows PowerShell: $env:DJANGO_DEBUG="1"
python manage.py makemigrations web  # first time only; creates web/migrations/0001_initial.py
python manage.py migrate
python manage.py test                # all tests should pass
python manage.py createsuperuser     # your admin login
python manage.py runserver           # http://127.0.0.1:8000
```

Admin (enquiries): http://127.0.0.1:8000/admin/

With the default `MAIL_BACKEND=console`, enquiry emails are printed in the terminal.

## Where things are

| Path | What it holds |
|---|---|
| `web/content.py` | All words, phone numbers, address, CAC number, hours. Edit here. |
| `web/templates/web/` | One template per page |
| `templates/base.html` | Header, footer, SEO tags |
| `static/css/site.css` | The whole design (colour tokens at the top) |
| `static/img/` | Team photos, icon, share image |
| `web/models.py`, `forms.py`, `views.py`, `mail.py` | Enquiry storage, spam protection, email |
| `web/tests.py` | Automated tests |
| `render.yaml` | Hosting set-up for Render |

## Before launch (marked CHECK in `web/content.py`)

CAC number, opening hours, address wording, retention period quoted in the privacy notice, a real screenshot of Hostel Meals, and a lawyer's look at the privacy notice.

## Deploy on Render

1. Push to GitHub. In Render choose New > Blueprint and pick the repository.
2. Fill the values Render asks for: `SITE_URL`, `DJANGO_ALLOWED_HOSTS`, `ADMIN_URL` (a path only you know), `RESEND_API_KEY`, `MAIL_FROM`.
3. Create the admin user once from the Render shell: `python manage.py createsuperuser`.
4. Add your domain in Render, then send a test enquiry and check it arrives.

The database is a SQLite file on the persistent disk (`/var/data`). Run one instance only. Delete old enquiries with `python manage.py purge_enquiries` (add `--dry-run` to preview).

## Not included yet

Two-factor login for the admin, self-hosted web font, analytics, Hausa pages, CMS (Wagtail). See the study document.
