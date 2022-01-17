from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

CODE_BYTES = getattr(settings, "GETIN_CODE_BYTES", 8)

default_subject = "Your invitation"

SITE_ID = getattr(settings, "SITE_ID", None)

if not SITE_ID:
    SITE_ID = getattr(settings, "GETIN_SITE_ID", None)

if not SITE_ID:
    raise ImproperlyConfigured("Please set SITE_ID or configure django.contrib.sites.")

EMAIL_SUBJECT = getattr(settings, "GETIN_EMAIL_SUBJECT", default_subject)
