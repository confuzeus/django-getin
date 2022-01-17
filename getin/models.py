import logging
from enum import IntEnum, auto

from django.conf import settings
from django.db import models
from django_fsm import FSMIntegerField, transition

log = logging.getLogger(__name__)


class InvitationState(IntEnum):
    UNSENT = auto()
    SENT = auto()
    CONSUMED = auto()
    EXPIRED = auto()


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

    def send_invitation(self):
        raise NotImplemented()

    class Meta:
        abstract = True


class EmailInvitation(Invitation):
    USER_RELATED_NAME = "getin_email_invitation"
    email = models.EmailField(unique=True)

    @transition(
        field="state",
        source=InvitationState.UNSENT.value,
        target=InvitationState.SENT.value,
    )
    def send_invitation(self):
        log.info(f"Invitation send to {self.email}")

    def __str__(self):
        return f"Email invitation for {self.email}."

    class Meta:
        db_table = "getin_email_invitations"
        indexes = [models.Index(fields=("email",))]
        ordering = ["-created_at"]
