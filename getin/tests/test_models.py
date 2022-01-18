import pytest
from getin.models import Invitation, InvitationState


@pytest.mark.django_db
def test_invitation_create():
    invitation = Invitation.create()
    assert invitation.state == InvitationState.UNSENT.value
    assert invitation._state.adding is False
