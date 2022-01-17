import secrets
import string

from getin import settings as app_settings


def generate_code():
    allowed_chars = string.ascii_uppercase + string.digits
    return "".join(
        secrets.choice(allowed_chars) for _ in range(app_settings.CODE_BYTES)
    )
