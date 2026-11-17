from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return ["home", "products", "hostel_meals", "services", "how_we_work", "team", "contact", "privacy"]

    def location(self, item):
        return reverse(item)
