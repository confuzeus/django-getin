from django.contrib import admin

from getin.models import Invitation


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    readonly_fields = ("user", "code", "state", "created_at")
