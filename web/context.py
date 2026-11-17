import json
from urllib.parse import quote

from django.conf import settings

from . import content


def _json_ld():
    site = content.SITE
    address = site["address_lines"]
    data = {
        "@context": "https://schema.org",
        "@type": ["Organization", "LocalBusiness"],
        "name": site["name"],
        "url": settings.SITE_URL,
        "email": site["email"],
        "telephone": site["phones"][0]["intl"],
        "description": site["description"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": ", ".join(address[:2]),
            "addressLocality": "Kano",
            "addressRegion": "Kano State",
            "addressCountry": "NG",
        },
        "founder": [{"@type": "Person", "name": p["name"]} for p in content.TEAM],
    }
    if site["opening_hours"]:
        data["openingHours"] = site["opening_hours"]
    # Escape "<" so the data can never close the script tag.
    return json.dumps(data).replace("<", "\\u003c")


def site(request):
    match = getattr(request, "resolver_match", None)
    return {
        "site": content.SITE,
        "nav": content.NAV,
        "current": match.url_name if match else "",
        "whatsapp_url": f"https://wa.me/{content.SITE['whatsapp']}?text={quote(content.SITE['whatsapp_text'])}",
        "canonical": settings.SITE_URL + request.path,
        "site_url": settings.SITE_URL,
        "json_ld": _json_ld(),
    }
