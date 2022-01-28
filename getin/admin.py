from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django_fsm import TransitionNotAllowed, can_proceed

from getin.forms import EmailInvitationForm
from getin.models import Invitation, InvitationState
from getin.utils import email_invitation


def _transition_queryset(
    modeladmin: admin.ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet[Invitation],
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
            elif method == InvitationState.SENT:

                def _send_func(code):
                    """
                    Pretend like we're sending an invitation.
                    :param code: Invitation code
                    :return: None
                    """
                    pass

                invitation.send_invitation(_send_func)
            invitation.full_clean()
            invitation.save()
        except TransitionNotAllowed as e:
            modeladmin.message_user(
                request, f"TransitionNotAllowed: {e}", level=messages.ERROR
            )
        except ValidationError as e:  # pragma: no cover
            modeladmin.message_user(
                request, f"ValidationError: {e}", level=messages.ERROR
            )
        except IntegrityError as e:  # pragma: no cover
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


@admin.action(description=_("Mark selected invitations as sent."))
def mark_as_sent(
    modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet
):
    _transition_queryset(
        modeladmin, request, queryset, InvitationState.SENT, force=True
    )


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ("code", "state", "created_at", "send_list_btn")
    date_hierarchy = "created_at"
    readonly_fields = ("user", "code", "state", "created_at")
    actions = [expire, force_expire, mark_as_sent]

    @admin.display(description=_("Send"))
    def send_list_btn(self, obj):
        html = ""
        if obj.state == InvitationState.UNSENT.value:
            invite_url = reverse_lazy("admin:email-invitation", kwargs={"pk": obj.pk})
            html += f"""<a href="{invite_url}">Send email</a>"""
        else:
            html += "-"
        return format_html(html)

    def get_urls(self):
        urls = super(InvitationAdmin, self).get_urls()
        extra_urls = [
            path(
                "send-email/<int:pk>/",
                self.admin_site.admin_view(self.send_email_view),
                name="email-invitation",
            ),
        ]
        return extra_urls + urls

    def send_email_view(self, request: HttpRequest, pk: int):
        invitation = get_object_or_404(Invitation, pk=pk)

        if not can_proceed(invitation.send_invitation):
            self.message_user(
                request,
                _(f"This invitation can't be sent because it's {invitation.state}."),
                level=messages.WARNING,
            )
            return redirect("admin:getin_invitation_changelist")
        form = None

        if request.method == "POST":

            form = EmailInvitationForm(request.POST)

            if form.is_valid():

                invitation.send_invitation(
                    email_invitation, email=form.cleaned_data["email"]
                )

                try:
                    invitation.full_clean()
                    invitation.save()
                    self.message_user(
                        request, _("Invitation sent."), level=messages.SUCCESS
                    )
                    return redirect("admin:getin_invitation_changelist")
                except ValidationError as e:  # pragma: no cover
                    self.message_user(
                        request, _(f"ValidationError: {e}"), level=messages.ERROR
                    )
                except IntegrityError as e:  # pragma: no cover
                    self.message_user(
                        request, _(f"IntegrityError: {e}"), level=messages.ERROR
                    )

        if form is None:
            form = EmailInvitationForm()

        context = dict(
            self.admin_site.each_context(request),
            invitation=invitation,
            subtitle=_("Send email invitation"),
            form=form,
        )
        return TemplateResponse(request, "getin/send_email_admin.html", context)

    def add_view(self, request: HttpRequest, form_url="", extra_context=None):

        if request.method == "POST":

            invitation = Invitation.create()

            self.message_user(
                request, f"Invitation {invitation.code} has been created."
            )
            return redirect(
                reverse_lazy(
                    "admin:getin_invitation_change", kwargs={"object_id": invitation.pk}
                )
            )

        context = dict(
            self.admin_site.each_context(request), subtitle=_("Create invitation")
        )
        return TemplateResponse(request, "getin/confirm_create.html", context)
