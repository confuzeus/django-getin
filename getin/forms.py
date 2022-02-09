from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django_fsm import can_proceed

from getin.models import Invitation
from getin.settings import CODE_BYTES


class InvitationCodeField(forms.CharField):
    """
    Form field to be used in forms that
    will cause an invitation to be consumed.
    Example: Registration form
    """

    def __init__(self, **kwargs):
        self.max_length = CODE_BYTES
        self.min_length = CODE_BYTES
        self.strip = True
        self.empty_value = ""
        super().__init__(
            max_length=self.max_length,
            min_length=self.min_length,
            strip=self.strip,
            empty_value=self.empty_value,
            **kwargs,
        )

    def clean(self, value):

        try:
            invitation = Invitation.objects.get(code=value)
        except Invitation.DoesNotExist:
            raise ValidationError(_("This invitation code doesn't exist."))

        if not can_proceed(invitation.consume):
            raise ValidationError(
                _(f"This invitation is unusable because it's {invitation.state}")
            )

        return super(InvitationCodeField, self).clean(value)


class EmailInvitationForm(forms.Form):
    email = forms.EmailField(help_text=_("Recipient's email address."))
