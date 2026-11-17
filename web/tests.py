import time

from django.test import TestCase
from django.urls import reverse

from .forms import make_token
from .models import Enquiry

PAGES = ["home", "products", "hostel_meals", "services", "how_we_work", "team", "contact", "privacy"]
FULL_NAME = "Uranium Jet Digital Solution"


def valid_post(**overrides):
    data = {
        "name": "Aisha Bello", "email": "aisha@example.com", "phone": "08000000000",
        "topic": "software", "message": "We would like a system for our school.",
        "website": "", "started": make_token(time.time() - 30),
    }
    data.update(overrides)
    return data


class PageTests(TestCase):
    def test_every_page_loads_with_full_name(self):
        for name in PAGES:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, FULL_NAME)

    def test_no_old_name_anywhere(self):
        for name in PAGES:
            response = self.client.get(reverse(name))
            self.assertNotContains(response, "Uranium Jet website")
            self.assertNotContains(response, "Uranium Jet Website")

    def test_each_page_has_one_h1(self):
        for name in PAGES:
            self.assertEqual(self.client.get(reverse(name)).content.decode().count("<h1"), 1, name)

    def test_whatsapp_link_uses_main_number_and_full_name(self):
        html = self.client.get(reverse("home")).content.decode()
        self.assertIn("https://wa.me/2349034097508?text=Hello%20Uranium%20Jet%20Digital%20Solution", html)

    def test_both_phone_numbers_shown(self):
        html = self.client.get(reverse("contact")).content.decode()
        self.assertIn("09034097508", html)
        self.assertIn("08145477724", html)

    def test_demo_link_is_present(self):
        self.assertContains(self.client.get(reverse("products")), "https://hostel-meals-demo.onrender.com")

    def test_404_page(self):
        response = self.client.get("/no-such-page/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "could not find", status_code=404)

    def test_healthz_robots_sitemap(self):
        self.assertEqual(self.client.get("/healthz").content, b"ok")
        self.assertIn("Sitemap:", self.client.get("/robots.txt").content.decode())
        sitemap = self.client.get("/sitemap.xml")
        self.assertEqual(sitemap.status_code, 200)
        self.assertIn(b"/products/hostel-meals/", sitemap.content)

    def test_security_headers(self):
        response = self.client.get(reverse("home"))
        policy = response["Content-Security-Policy"]
        self.assertIn("script-src 'self'", policy)
        self.assertNotIn("unsafe-inline", policy)
        self.assertEqual(response["X-Frame-Options"], "DENY")
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")

    def test_no_inline_scripts_or_styles(self):
        for name in PAGES:
            html = self.client.get(reverse(name)).content.decode()
            self.assertNotIn(" style=", html, name)
            self.assertNotIn("onclick=", html, name)
            for chunk in html.split("<script")[1:]:
                tag = chunk.split(">")[0]
                self.assertTrue("src=" in tag or "application/ld+json" in tag, name)


class ContactTests(TestCase):
    def test_valid_enquiry_is_saved_and_redirects_303(self):
        response = self.client.post(reverse("contact"), valid_post())
        self.assertEqual(response.status_code, 303)
        self.assertEqual(Enquiry.objects.count(), 1)
        enquiry = Enquiry.objects.get()
        self.assertEqual(enquiry.email, "aisha@example.com")
        self.assertTrue(enquiry.emailed)  # console backend counts as sent

    def test_thank_you_page_shows_once(self):
        self.client.post(reverse("contact"), valid_post())
        self.assertEqual(self.client.get(reverse("contact_sent")).status_code, 200)
        self.assertEqual(self.client.get(reverse("contact_sent")).status_code, 302)

    def test_thank_you_page_needs_a_submission(self):
        self.assertEqual(self.client.get(reverse("contact_sent")).status_code, 302)

    def test_honeypot_saves_nothing(self):
        response = self.client.post(reverse("contact"), valid_post(website="http://spam.example"))
        self.assertEqual(response.status_code, 303)
        self.assertEqual(Enquiry.objects.count(), 0)

    def test_too_fast_saves_nothing(self):
        self.client.post(reverse("contact"), valid_post(started=make_token()))
        self.assertEqual(Enquiry.objects.count(), 0)

    def test_missing_token_saves_nothing(self):
        self.client.post(reverse("contact"), valid_post(started=""))
        self.assertEqual(Enquiry.objects.count(), 0)

    def test_invalid_form_shows_errors(self):
        response = self.client.post(reverse("contact"), valid_post(email="not-an-email", message="hi"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter an email address")
        self.assertContains(response, "Write at least a sentence")
        self.assertEqual(Enquiry.objects.count(), 0)

    def test_rate_limit(self):
        for _ in range(5):
            self.assertEqual(self.client.post(reverse("contact"), valid_post()).status_code, 303)
        response = self.client.post(reverse("contact"), valid_post())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "several messages")
        self.assertEqual(Enquiry.objects.count(), 5)

    def test_topic_preselected_from_link(self):
        self.assertContains(self.client.get(reverse("contact") + "?topic=hostel-meals"), 'value="hostel-meals" selected')

    def test_enquiry_survives_failed_email(self):
        from django.test import override_settings
        with override_settings(MAIL_BACKEND="resend", RESEND_API_KEY="", MAIL_FROM=""):
            self.client.post(reverse("contact"), valid_post())
        enquiry = Enquiry.objects.get()
        self.assertFalse(enquiry.emailed)
