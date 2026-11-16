# Uranium Jet Digital Solution: company website

Flask (Python) site with a working contact form and WhatsApp buttons. No database, no JavaScript framework, no build step.

## Run it on your computer

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
export FLASK_DEBUG=1 SECRET_KEY=dev MAIL_BACKEND=console
flask --app wsgi run          # http://127.0.0.1:5000
pytest                        # 38 tests
```

With `MAIL_BACKEND=console`, contact-form messages are printed in the terminal instead of emailed.

## Edit the content

Everything you will want to change is in **`content.py`**: phone numbers, WhatsApp number, address, services, product text, the four work steps, team and values. Team photos are in `static/img/`.

Check these before launch (marked `CHECK` in `content.py`):
- **Phone numbers.** The old site listed `0814547724` (only 10 digits, so probably a typo) and the flyer listed `08087314361`. The new site uses `09034097508` and `08087314361`. Confirm both, and confirm which one WhatsApp should go to.
- **Address and email** were copied from your old site and flyer.
- **Team bios** are short and written from what I know of you and Engr. Ahmad. Edit them freely.
- **Hostel Meals text** describes what you told me about the system. Remove anything you do not want to promise to clients.

## Pages

| URL | Purpose |
|---|---|
| `/` | Offer, live demo, services, product, process, team, contact prompts |
| `/products` | Hostel Meals with demo link, plus two planned products marked "In planning" |
| `/products/hostel-meals` | Feature list, demo link, WhatsApp enquiry |
| `/services` | Software and web, IT support, print and design, cyber café |
| `/how-we-work` | Four steps, with what you need from the client at each |
| `/team` | Leadership, mission, vision, values |
| `/contact` | Working form, WhatsApp, phone, email, address and map link |

## Deploy on Render (recommended)

1. Put this folder in a GitHub repository (a new one, or replace the contents of `uraniumjet/uraniumjet_`; GitHub Pages cannot run Python, so turn Pages off for that repo).
2. In Render: **New > Blueprint**, choose the repository. `render.yaml` sets up the service on the Starter plan.
3. Set the secret values Render asks for:
   - `SITE_URL`: your final address, for example `https://www.yourdomain.com`
   - `RESEND_API_KEY` and `MAIL_FROM` (see "Email" below)
4. Add your domain under the service's **Settings > Custom Domains** and create the DNS records Render shows.
5. Open `/contact`, send yourself a test message, and click the WhatsApp button.

`SECRET_KEY` is generated for you. The site refuses to start without one in production.

## Email for the contact form

The form sends through the Resend HTTPS API (works on any host). Setup:
1. Create a Resend account, add your domain, and add the DNS records it shows.
2. Create an API key. Set `RESEND_API_KEY`, and `MAIL_FROM` such as `Uranium Jet Website <contact@yourdomain.com>`.
3. `MAIL_TO` is where messages arrive (default: your Gmail). Replying to a message goes to the visitor, because their address is set as Reply-To.

Without a verified domain Resend can only send test mail to your own account, so do step 1 before launch. As an alternative that needs no domain, set `MAIL_BACKEND=smtp` with a Gmail app password (`SMTP_HOST=smtp.gmail.com`, `SMTP_PORT=587`).

If mail is not configured or fails, visitors see a clear message pointing them to WhatsApp, and nothing is silently lost.

## Spam and safety built into the form

Hidden honeypot field, per-visit token, minimum fill time, 5 messages per 10 minutes per address, input length limits, and header-injection protection. The site also sends strict security headers (no inline scripts or styles are used, so the Content Security Policy can stay tight). The rate limiter keeps counts per server process, which is fine for a single small instance.

## Costs

See the table in the chat summary. Prices were taken from third-party summaries dated October 2026 because the providers' own pricing pages could not be fetched; confirm them on the provider pages before paying.
