import logging
from enum import IntEnum

from django.conf import settings
from django.db import models
from django_fsm import FSMIntegerField, transition

log = logging.getLogger(__name__)


class InvitationState(IntEnum):
    UNSENT = 1
    SENT = 2
    CONSUMED = 3
    EXPIRED = 4


class Invitation(models.Model):
    USER_RELATED_NAME = "getin_invitation"
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name=USER_RELATED_NAME,
        null=True,
        blank=True,
    )
    code = models.CharField(max_length=64, unique=True)
    state = FSMIntegerField(default=InvitationState.UNSENT.value)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    def send_invitation(self):
        raise NotImplemented()

    def __str__(self):
        return self.code

    class Meta:
        db_table = "getin_invitations"
        indexes = [models.Index(fields=("email",))]
        ordering = ["-created_at"]
