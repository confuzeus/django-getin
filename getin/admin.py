from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django_fsm import TransitionNotAllowed

from getin.models import Invitation, InvitationState


def _transition_queryset(
    modeladmin: admin.ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet,
    method: InvitationState,
    **kwargs,
):
    for invitation in queryset:
        try:
            if method == InvitationState.EXPIRED:
                if kwargs.get("force"):
                    invitation.force_expire()
                else:
                    invitation.expire()
            invitation.full_clean()
            invitation.save()
        except TransitionNotAllowed as e:
            modeladmin.message_user(
                request, f"TransitionNotAllowed: {e}", level=messages.ERROR
            )
        except ValidationError as e:
            modeladmin.message_user(
                request, f"ValidationError: {e}", level=messages.ERROR
            )
        except IntegrityError as e:
            modeladmin.message_user(
                request, f"IntegrityError: {e}", level=messages.ERROR
            )


@admin.action(description=_("Expire selected invitations."))
def expire(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    _transition_queryset(modeladmin, request, queryset, InvitationState.EXPIRED)


@admin.action(description=_("Force selected invitations to expire."))
def force_expire(
    modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet
):
    _transition_queryset(
        modeladmin, request, queryset, InvitationState.EXPIRED, force=True
    )


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ("code", "state", "created_at")
    date_hierarchy = "created_at"
    readonly_fields = ("user", "code", "state", "created_at")
    actions = [expire, force_expire]
