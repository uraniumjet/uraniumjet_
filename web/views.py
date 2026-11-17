import hashlib
from datetime import timedelta

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from . import content
from .forms import ContactForm, make_token
from .mail import notify
from .models import Enquiry

RATE_LIMIT = 5          # enquiries
RATE_WINDOW_MINUTES = 10


def home(request):
    return render(request, "web/home.html", {
        "groups": content.SERVICE_GROUPS, "product": content.PRODUCT_HOSTEL,
        "steps": content.PROCESS, "team": content.TEAM, "facts": content.HOME_FACTS,
    })


def products(request):
    return render(request, "web/products.html", {"product": content.PRODUCT_HOSTEL, "planned": content.PRODUCTS_PLANNED})


def hostel_meals(request):
    return render(request, "web/hostel_meals.html", {"product": content.PRODUCT_HOSTEL})


def services(request):
    return render(request, "web/services.html", {"groups": content.SERVICE_GROUPS})


def how_we_work(request):
    return render(request, "web/how_we_work.html", {"steps": content.PROCESS})


def team(request):
    return render(request, "web/team.html", {"team": content.TEAM, "values": content.VALUES})


def privacy(request):
    return render(request, "web/privacy.html")


def _ip_hash(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    ip = forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR", "")
    return hashlib.sha256(f"{ip}|{settings.SECRET_KEY}".encode()).hexdigest()


def _sent(request):
    """Redirect after posting (status 303), so a refresh cannot send the form again."""
    request.session["enquiry_sent"] = True
    response = redirect(reverse("contact_sent"))
    response.status_code = 303
    return response


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            if form.looks_like_bot():
                return _sent(request)  # show bots the normal result and save nothing
            ip_hash = _ip_hash(request)
            since = timezone.now() - timedelta(minutes=RATE_WINDOW_MINUTES)
            if Enquiry.objects.filter(ip_hash=ip_hash, created_at__gte=since).count() >= RATE_LIMIT:
                form.add_error(None, "You have sent several messages in a short time. Please wait a few minutes, or message us on WhatsApp.")
            else:
                data = form.cleaned_data
                enquiry = Enquiry.objects.create(
                    name=data["name"], email=data["email"], phone=data["phone"],
                    topic=data["topic"], message=data["message"], ip_hash=ip_hash,
                )
                enquiry.emailed = notify(enquiry)
                enquiry.save(update_fields=["emailed"])
                return _sent(request)
        # Invalid or rate limited: show the form again with a fresh token.
        form.data = form.data.copy()
        form.data["started"] = make_token()
    else:
        topic = request.GET.get("topic", "")
        valid = {value for value, _label in content.CONTACT_TOPICS}
        form = ContactForm(initial={"topic": topic if topic in valid else "", "started": make_token()})
    return render(request, "web/contact.html", {"form": form})


def contact_sent(request):
    if not request.session.pop("enquiry_sent", False):
        return redirect("contact")
    return render(request, "web/contact_sent.html")


def healthz(request):
    return HttpResponse("ok", content_type="text/plain")


def robots_txt(request):
    body = f"User-agent: *\nAllow: /\nDisallow: /{settings.ADMIN_URL}\n\nSitemap: {settings.SITE_URL}/sitemap.xml\n"
    return HttpResponse(body, content_type="text/plain")
