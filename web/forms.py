import time

from django import forms
from django.core import signing

from .content import CONTACT_TOPICS

MIN_FILL_SECONDS = 3
MAX_AGE_SECONDS = 2 * 60 * 60
_signer = signing.TimestampSigner(salt="contact-form")


def make_token(started_at=None):
    """A signed timestamp put in the form so we can tell how long the visitor took."""
    return _signer.sign(str(int(started_at if started_at is not None else time.time())))


def _input(**attrs):
    return forms.TextInput(attrs=attrs)


class ContactForm(forms.Form):
    name = forms.CharField(
        label="Your name", max_length=120,
        widget=_input(autocomplete="name"),
        error_messages={"required": "Enter your name."},
    )
    email = forms.EmailField(
        label="Email address", max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
        error_messages={"required": "Enter your email address.", "invalid": "Enter an email address such as name@example.com."},
    )
    phone = forms.CharField(
        label="Phone or WhatsApp number (optional)", max_length=40, required=False,
        widget=forms.TextInput(attrs={"autocomplete": "tel", "inputmode": "tel"}),
    )
    topic = forms.ChoiceField(
        label="What is this about?", choices=[("", "Choose a topic")] + CONTACT_TOPICS,
        error_messages={"required": "Choose a topic.", "invalid_choice": "Choose a topic from the list."},
    )
    message = forms.CharField(
        label="Your message", min_length=10, max_length=4000,
        widget=forms.Textarea(attrs={"rows": 6}),
        error_messages={
            "required": "Write a short message.",
            "min_length": "Write at least a sentence so we can help.",
            "max_length": "Keep the message under 4,000 characters.",
        },
    )
    # Spam traps. Real visitors never see or fill the first one.
    website = forms.CharField(required=False, label="Leave this empty", widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}))
    started = forms.CharField(required=False, widget=forms.HiddenInput)

    def full_clean(self):
        super().full_clean()
        for name in self.errors:
            if name in self.fields:
                self.fields[name].widget.attrs["aria-invalid"] = "true"
                self.fields[name].widget.attrs["aria-describedby"] = f"id_{name}_error"

    def looks_like_bot(self):
        """True when the honeypot is filled, or the form was sent too fast or with a bad or old token."""
        data = self.cleaned_data
        if data.get("website"):
            return True
        try:
            started = int(_signer.unsign(data.get("started", ""), max_age=MAX_AGE_SECONDS))
        except (signing.BadSignature, ValueError):
            return True
        return time.time() - started < MIN_FILL_SECONDS
