import pytest

from getin.admin import _transition_queryset
from getin.models import Invitation, InvitationState


@pytest.mark.django_db
def test_transition_force_expire(admin_user, invitation_admin, unsent_invitation, rf):
    qs = Invitation.objects.all()

    transition_method = InvitationState.EXPIRED
    request = rf.get("/")
    request.user = admin_user
    _transition_queryset(invitation_admin, request, qs, transition_method, force=True)

    for invitation in Invitation.objects.all():
        assert invitation.state == InvitationState.EXPIRED.value
