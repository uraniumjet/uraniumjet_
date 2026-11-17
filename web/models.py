from django.db import models

from .content import CONTACT_TOPICS


class Enquiry(models.Model):
    """A message sent through the contact form. It is saved before any email is attempted."""

    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    topic = models.CharField(max_length=30, choices=CONTACT_TOPICS)
    message = models.TextField(max_length=4000)
    emailed = models.BooleanField(default=False, help_text="Whether the notification email was sent.")
    handled = models.BooleanField(default=False, help_text="Tick when someone has replied.")
    notes = models.TextField(blank=True, help_text="Internal notes. Never shown to the visitor.")
    ip_hash = models.CharField(max_length=64, blank=True, editable=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "enquiries"

    def __str__(self):
        return f"{self.name} ({self.get_topic_display()}) on {self.created_at:%d %b %Y}"
