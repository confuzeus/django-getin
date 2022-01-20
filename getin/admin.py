from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from getin.models import Invitation


@admin.action(description=_("Expire selected invitations."))
def expire(*args):
    for invitation in args[2]:
        invitation.expire()
        invitation.full_clean()
        invitation.save()


@admin.action(description=_("Force selected invitations to expire."))
def force_expire(*args):
    for invitation in args[2]:
        invitation.force_expire()
        invitation.full_clean()
        invitation.save()


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    readonly_fields = ("user", "code", "state", "created_at")
    actions = [expire, force_expire]
