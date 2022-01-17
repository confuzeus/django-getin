import logging
import secrets
import string
from enum import Enum

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMField, transition

from getin import settings as app_settings

log = logging.getLogger(__name__)


class InvitationState(Enum):
    UNSENT = "Unsent"
    SENT = "Sent"
    CONSUMED = "Consumed"
    EXPIRED = "Expired"


class Invitation(models.Model):
    USER_RELATED_NAME = "getin_invitation"
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name=USER_RELATED_NAME,
        null=True,
        blank=True,
    )
    code = models.CharField(
        max_length=64, unique=True, verbose_name=_("Invitation code")
    )
    state = FSMField(default=InvitationState.UNSENT.value)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def generate_code():
        allowed_chars = string.ascii_uppercase + string.digits
        return "".join(
            secrets.choice(allowed_chars) for _ in range(app_settings.CODE_BYTES)
        )

    @classmethod
    def create(cls):
        code = cls.generate_code()
        invitation = cls(code=code)
        invitation.full_clean()
        invitation.save()
        return invitation

    @transition(
        field=state,
        source=InvitationState.SENT.value,
        target=InvitationState.CONSUMED.value,
    )
    def consume(self, valid_user):
        """
        Set the state to consumed, which means
        that a user signed up using this invitation code.
        :return: None
        """
        self.user = valid_user
        log.info(f"{valid_user} consumed their invitation.")

    @transition(field=state, source="*", target=InvitationState.EXPIRED.value)
    def force_expire(self):
        """
        Forcefully set the invitation state to expired.
        :return: None
        """
        log.info(f"Invitation {self.pk} has been forced to expire.")

    @transition(
        field="state",
        source=InvitationState.UNSENT.value,
        target=InvitationState.SENT.value,
    )
    def send_invitation(self, func):
        func(self.code)

    def __str__(self):
        return self.code

    class Meta:
        db_table = "getin_invitations"
        indexes = [models.Index(fields=("email", "created_at"))]
        ordering = ["-created_at"]
