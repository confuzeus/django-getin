import logging

from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.template.loader import render_to_string

from getin import settings as app_settings

log = logging.getLogger(__name__)


def email_invitation(code, **kwargs):
    email = kwargs.pop("email")

    try:
        site = Site.objects.get(pk=app_settings.SITE_ID)
    except Site.DoesNotExist:
        site = None
    ctx = {"code": code, "site": site}
    message = render_to_string("getin/invitation_email.txt", ctx)
    html_message = render_to_string("getin/invitation_email.html", ctx)

    send_mail(
        subject=app_settings.EMAIL_SUBJECT,
        message=message,
        from_email=None,
        recipient_list=[
            email,
        ],
        html_message=html_message,
    )
    log.info(f"Invitation emailed to {email}")
