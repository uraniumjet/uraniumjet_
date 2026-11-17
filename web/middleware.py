from django.conf import settings

from .content import SITE


class SecurityHeadersMiddleware:
    """Strict Content Security Policy for the public site. The admin keeps Django's own defaults."""

    def __init__(self, get_response):
        self.get_response = get_response
        demo_origin = "/".join(SITE["demo_url"].split("/")[:3])
        self.policy = "; ".join([
            "default-src 'self'",
            "script-src 'self'",
            "style-src 'self'",
            "img-src 'self' data:",
            f"connect-src 'self' {demo_origin}",
            "font-src 'self'",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'none'",
        ])

    def __call__(self, request):
        response = self.get_response(request)
        if not request.path.startswith("/" + settings.ADMIN_URL):
            response.headers.setdefault("Content-Security-Policy", self.policy)
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=()")
        return response
