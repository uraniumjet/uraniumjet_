from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from web.sitemaps import StaticSitemap

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": {"pages": StaticSitemap}}, name="sitemap"),
    path("", include("web.urls")),
]
