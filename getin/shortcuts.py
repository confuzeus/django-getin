from enum import Enum, auto
from typing import Optional
from django.utils.translation import gettext_lazy as _

from getin.models import EmailInvitation
from getin.utils import generate_code


class InvitationKind(Enum):
    EMAIL = auto()


def create_invitation(
    kind: InvitationKind = InvitationKind.EMAIL, valid_email: Optional[str] = None
):

    if kind is InvitationKind.EMAIL:
        if not valid_email:
            raise AttributeError(_("Please provide an email address."))
        code = generate_code()
        invitation = EmailInvitation(code=code, email=valid_email)
    else:
        raise AttributeError(_("Unknown kind of invitation."))
    invitation.full_clean()
    invitation.save()
    return invitation
