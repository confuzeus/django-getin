import pytest
from django import forms

from getin.forms import InvitationCodeField


class RegistrationForm(forms.Form):
    invitation_code = InvitationCodeField()


@pytest.mark.parametrize(
    "invitation, result",
    [
        ("unsent_invitation", False),
        ("sent_invitation", True),
        ("consumed_invitation", False),
        ("expired_invitation", False),
    ],
)
def test_invitation_code_field(invitation, result, request):
    form = RegistrationForm(
        {"invitation_code": request.getfixturevalue(invitation).code}
    )
    assert form.is_valid() is result
