import pytest

from getin.admin import _transition_queryset
from getin.models import Invitation, InvitationState


@pytest.mark.django_db
def test_transition_force_expire(admin_request, invitation_admin, unsent_invitation):
    qs = Invitation.objects.all()

    transition_method = InvitationState.EXPIRED
    _transition_queryset(
        invitation_admin, admin_request, qs, transition_method, force=True
    )

    for invitation in Invitation.objects.all():
        assert invitation.state == InvitationState.EXPIRED.value


@pytest.mark.django_db
def test_transition_expire(admin_request, invitation_admin, sent_invitation):
    qs = Invitation.objects.all()

    transition_method = InvitationState.EXPIRED
    _transition_queryset(invitation_admin, admin_request, qs, transition_method)

    for invitation in Invitation.objects.all():
        assert invitation.state == InvitationState.EXPIRED.value
