from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.products, name="products"),
    path("products/hostel-meals/", views.hostel_meals, name="hostel_meals"),
    path("services/", views.services, name="services"),
    path("how-we-work/", views.how_we_work, name="how_we_work"),
    path("team/", views.team, name="team"),
    path("contact/", views.contact, name="contact"),
    path("contact/sent/", views.contact_sent, name="contact_sent"),
    path("privacy/", views.privacy, name="privacy"),
    path("healthz", views.healthz, name="healthz"),
    path("robots.txt", views.robots_txt, name="robots"),
]
