from django.conf import settings
from django.contrib.sites.models import Site

CODE_BYTES = getattr(settings, "GETIN_CODE_BYTES", 8)

SITE_ID = getattr(settings, "SITE_ID", None)

if not SITE_ID:
    SITE_ID = getattr(settings, "GETIN_SITE_ID", None)


default_subject = "You've been invited"

if SITE_ID:
    try:
        site = Site.objects.get(pk=SITE_ID)
    except Site.DoesNotExist:
        site = None

    if site:
        default_subject += f"to {site.name}"


EMAIL_SUBJECT = getattr(settings, "GETIN_EMAIL_SUBJECT", default_subject)
