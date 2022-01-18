from unittest.mock import MagicMock

import pytest
from django_fsm import TransitionNotAllowed

from getin.models import Invitation, InvitationState


@pytest.mark.django_db
def test_invitation_create():
    invitation = Invitation.create()
    assert invitation.state == InvitationState.UNSENT.value
    assert invitation._state.adding is False


@pytest.mark.django_db
def test_invitation_consume_when_unsent(unsent_invitation, user):
    with pytest.raises(TransitionNotAllowed):
        unsent_invitation.consume(user)


@pytest.mark.django_db
def test_send_invitation(unsent_invitation, fake):
    send_fn = MagicMock()
    unsent_invitation.send_invitation(send_fn)
    send_fn.assert_called()
    assert unsent_invitation.state == InvitationState.SENT.value

    # Should not be saved yet
    unsent_invitation.refresh_from_db()
    assert unsent_invitation.state == InvitationState.UNSENT.value


@pytest.mark.django_db
def test_invitation_consume_when_sent(sent_invitation, user):
    sent_invitation.consume(user)

    assert sent_invitation.state == InvitationState.CONSUMED.value
    assert sent_invitation.user == user

    # Should not be saved yet
    sent_invitation.refresh_from_db()
    assert sent_invitation.state == InvitationState.SENT.value
    assert sent_invitation.user is None


@pytest.mark.django_db
def test_invitation_force_expire(sent_invitation):
    sent_invitation.force_expire()
    assert sent_invitation.state == InvitationState.EXPIRED.value

    # Should not be saved yet
    sent_invitation.refresh_from_db()
    assert sent_invitation.state == InvitationState.SENT.value


@pytest.mark.django_db
def test_invitation_str(unsent_invitation):
    assert str(unsent_invitation) == unsent_invitation.code
