from django import forms
from django.utils.translation import gettext_lazy as _


class EmailInvitationForm(forms.Form):
    email = forms.EmailField(help_text=_("Recipient's email address."))
