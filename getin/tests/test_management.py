from unittest.mock import patch

import pytest
from django.core.management import call_command

from getin.models import Invitation, InvitationState


@pytest.mark.django_db
def test_create_invitations():
    invitations_count = Invitation.objects.count()
    assert invitations_count == 0

    call_command("getin", "--create")
    invitations_count = Invitation.objects.count()
    assert invitations_count == 1

    Invitation.objects.all().delete()

    call_command("getin", "--create", "--count", "10")
    invitations_count = Invitation.objects.count()
    assert invitations_count == 10


@pytest.mark.django_db
def test_expire_invitation(sent_invitation):
    call_command("getin", "--expire", "--id", sent_invitation.pk)
    sent_invitation.refresh_from_db()
    assert sent_invitation.state == InvitationState.EXPIRED.value


@pytest.mark.django_db
def test_expire_invitations():
    def _create():
        for _ in range(10):
            Invitation.create()

    _create()

    def send(*args, **kwargs):
        pass

    def _send():

        for invitation in Invitation.objects.all():
            invitation.send_invitation(send)
            invitation.save()

    _send()
    call_command("getin", "--expire", "--all", state=InvitationState.SENT.value)

    for invitation in Invitation.objects.all():
        assert invitation.state == InvitationState.EXPIRED.value

    Invitation.objects.all().delete()

    _create()

    _send()

    with patch("builtins.input") as mock_input:
        mock_input.side_effect = "y"
        call_command("getin", "--expire", "--all")

        for invitation in Invitation.objects.all():
            assert invitation.state == InvitationState.EXPIRED.value

        Invitation.objects.all().delete()

        mock_input.side_effect = "n"

        _create()
        _send()
        call_command("getin", "--expire", "--all")
        for invitation in Invitation.objects.all():
            assert invitation.state == InvitationState.SENT.value

        Invitation.objects.all().delete()

        mock_input.side_effect = "y"

        _create()
        call_command("getin", "--force-expire", "--all")
        for invitation in Invitation.objects.all():
            assert invitation.state == InvitationState.EXPIRED.value


@pytest.mark.django_db
def test_send_invitation(unsent_invitation):

    with patch("getin.management.commands.getin.email_invitation") as mock_send_fn:

        call_command(
            "getin", "--send", "--id", unsent_invitation.pk, "--email", "john@smith.com"
        )
        mock_send_fn.assert_called()
        mock_send_fn.assert_called_with(unsent_invitation.code, email="john@smith.com")
        unsent_invitation.refresh_from_db()
        assert unsent_invitation.state == InvitationState.SENT.value
