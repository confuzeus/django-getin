from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured

CODE_BYTES = getattr(settings, "GETIN_CODE_BYTES", 8)

default_subject = "You've been invited"

SITE_ID = getattr(settings, "SITE_ID", None)

if not SITE_ID:
    SITE_ID = getattr(settings, "GETIN_SITE_ID", None)

if not SITE_ID:
    raise ImproperlyConfigured("Please set SITE_ID or configure django.contrib.sites.")


try:
    site = Site.objects.get(pk=SITE_ID)
except Site.DoesNotExist:
    raise ValueError(f"Couldn't find a site with id {SITE_ID}.")


default_subject += f"to {site.name}"


EMAIL_SUBJECT = getattr(settings, "GETIN_EMAIL_SUBJECT", default_subject)
