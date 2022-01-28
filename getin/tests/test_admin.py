from unittest.mock import MagicMock

import pytest
from django.urls import reverse

from getin.admin import _transition_queryset, expire, force_expire, mark_as_sent
from getin.forms import EmailInvitationForm
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

    for invitation in qs:
        assert invitation.state == InvitationState.EXPIRED.value


@pytest.mark.django_db
def test_transition_not_allowed(admin_request, invitation_admin, unsent_invitation):
    qs = Invitation.objects.all()

    transition_method = InvitationState.EXPIRED

    mock_message_user = MagicMock()
    invitation_admin.message_user = mock_message_user
    _transition_queryset(invitation_admin, admin_request, qs, transition_method)
    mock_message_user.assert_called()


@pytest.mark.django_db
def test_transition_mark_sent(admin_request, invitation_admin, unsent_invitation):
    qs = Invitation.objects.all()

    transition_method = InvitationState.SENT
    _transition_queryset(invitation_admin, admin_request, qs, transition_method)

    for invitation in qs:
        assert invitation.state == InvitationState.SENT.value


@pytest.mark.django_db
def test_admin_expire_action(admin_request, invitation_admin, sent_invitation):
    qs = Invitation.objects.all()

    expire(invitation_admin, admin_request, qs)

    for invitation in qs:
        assert invitation.state == InvitationState.EXPIRED.value


@pytest.mark.django_db
def test_admin_force_expire_action(admin_request, invitation_admin, unsent_invitation):

    qs = Invitation.objects.all()

    force_expire(invitation_admin, admin_request, qs)

    for invitation in qs:
        assert invitation.state == InvitationState.EXPIRED.value


@pytest.mark.django_db
def test_admin_mark_as_sent_action(admin_request, invitation_admin, unsent_invitation):

    qs = Invitation.objects.all()

    mark_as_sent(invitation_admin, admin_request, qs)

    for invitation in qs:
        assert invitation.state == InvitationState.SENT.value


@pytest.mark.django_db
def test_admin_send_list_btn_html_unsent(invitation_admin, unsent_invitation):
    invite_url = reverse("admin:email-invitation", kwargs={"pk": unsent_invitation.pk})
    send_list_btn = invitation_admin.send_list_btn(unsent_invitation)
    assert send_list_btn == f"""<a href="{invite_url}">Send email</a>"""


@pytest.mark.django_db
def test_admin_send_list_btn_html_sent(invitation_admin, sent_invitation):
    send_list_btn = invitation_admin.send_list_btn(sent_invitation)
    assert send_list_btn == "-"


@pytest.mark.django_db
def test_admin_send_email_view(
    admin_user, client, fake, invitation_admin, unsent_invitation
):

    client.force_login(admin_user)

    send_invitation_url = reverse(
        "admin:email-invitation", kwargs={"pk": unsent_invitation.pk}
    )

    response = client.get(send_invitation_url)

    form = response.context.get("form")
    assert form is not None

    assert isinstance(form, EmailInvitationForm)

    # Post with valid data

    client.post(send_invitation_url, {"email": fake.ascii_email()})

    unsent_invitation.refresh_from_db()

    assert unsent_invitation.state == InvitationState.SENT.value

    # Post with invalid data

    invitation = Invitation.create()

    response = client.post(
        reverse("admin:email-invitation", kwargs={"pk": invitation.pk}),
        {"email": "notemail"},
    )

    assert len(response.context["form"].errors) > 0
    invitation.refresh_from_db()
    assert invitation.state == InvitationState.UNSENT.value
