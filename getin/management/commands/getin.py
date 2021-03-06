from typing import Optional

from django.core.exceptions import ValidationError
from django.core.management import BaseCommand, CommandError
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _
from django_fsm import TransitionNotAllowed

from getin.models import Invitation, InvitationState
from getin.utils import email_invitation


class Command(BaseCommand):
    help = _("Manage invitations")

    def _create_invitations(self, count: Optional[int] = None):
        def _create():
            invitation = Invitation.create()

            self.stdout.write(
                self.style.SUCCESS(
                    _(f'Invitation with ID "{invitation.pk}" has been created.')
                )
            )

        if count:

            for __ in range(count):
                _create()

        else:
            _create()

    @staticmethod
    def _get_invitation(id_: int):
        try:
            invitation = Invitation.objects.get(pk=id_)
        except Invitation.DoesNotExist:
            raise CommandError(_(f'Invitation with ID "{id_}" doesn\'t exist.'))

        return invitation

    def _state_transition(
        self,
        obj: Invitation,
        target: InvitationState,
        force: Optional[bool] = False,
        **kwargs,
    ):
        try:
            if target == InvitationState.EXPIRED:
                if force:
                    obj.force_expire()
                else:
                    obj.expire()
            elif target == InvitationState.SENT:
                func = kwargs.pop("send_func")
                email = kwargs.pop("email")
                obj.send_invitation(func, email=email)
            else:
                raise CommandError(_(f'"{target}" is an unknown target state'))
            obj.full_clean()
            obj.save()
        except TransitionNotAllowed as e:
            raise CommandError(e)
        except ValidationError as e:
            raise CommandError(e)
        except IntegrityError as e:
            raise CommandError(e)
        self.stdout.write(_(f'Invitation with ID "{obj.pk}" has expired.'))

    def _expire_invitations(
        self,
        id_: Optional[int] = None,
        all_: Optional[bool] = None,
        state: Optional[str] = None,
        force: Optional[bool] = False,
    ):
        if id_:
            invitation = self._get_invitation(id_)
            self._state_transition(invitation, InvitationState.EXPIRED, force)
            return

        invitations = None
        if all_ and state:
            invitations = Invitation.objects.filter(state=state)

        elif all_ and not state:
            cont = input(_("This will expire all invitations. Continue? (y/n)"))
            if cont.strip().lower() == "y":
                invitations = Invitation.objects.all()
            else:
                self.stdout.write("Aborted.")
                return

        if invitations:
            for invitation in invitations:
                self._state_transition(invitation, InvitationState.EXPIRED, force)
            return
        self.stdout.write(self.style.WARNING(_("No invitations found.")))

    def _send_invitation(self, id_, method: str = "email", **kwargs):

        invitation = self._get_invitation(id_)

        if method == "email":
            self._state_transition(
                invitation,
                InvitationState.SENT,
                send_func=email_invitation,
                email=kwargs.pop("email"),
            )
        else:
            raise CommandError(
                _(f'I don\'t know how to send invitations using "{method}".')
            )

    def add_arguments(self, parser):
        action_group = parser.add_mutually_exclusive_group()
        action_group.add_argument(
            "--create",
            action="store_true",
            default=False,
            help=_("Create invitations."),
        )

        action_group.add_argument(
            "--expire", action="store_true", help=_("Expire invitations.")
        )
        action_group.add_argument(
            "--send", action="store_true", help=_("Send an invitation.")
        )
        action_group.add_argument(
            "--force-expire",
            action="store_true",
            help=_("Force invitations to expire."),
        )

        amount_group = parser.add_mutually_exclusive_group()

        amount_group.add_argument(
            "--count", default=0, type=int, help=_("Number of invitations to create")
        )
        amount_group.add_argument(
            "--id",
            type=int,
            help=_("The id of a specific invitation you want to act on."),
        )
        amount_group.add_argument(
            "--all", action="store_true", help=_("Act on all invitations.")
        )

        parser.add_argument(
            "--state",
            choices=(
                InvitationState.UNSENT.value,
                InvitationState.SENT.value,
                InvitationState.CONSUMED.value,
                InvitationState.EXPIRED.value,
            ),
            help=(_("Filter the state of the invitation(s).")),
        )
        parser.add_argument(
            "--email", type=str, help=_("The email address to send the invitation to.")
        )

    def handle(self, *args, **options):

        create = options.get("create")
        expire = options.get("expire")
        force_expire = options.get("force_expire")
        send = options.get("send")

        count = options.get("count")
        id_ = options.get("id")
        all_ = options.get("all")

        state = options.get("state")
        email = options.get("email")

        if create:
            return self._create_invitations(count)

        if expire:
            return self._expire_invitations(id_, all_, state)

        if force_expire:
            return self._expire_invitations(id_, all_, state, force=True)

        if send:
            if not email:
                raise CommandError(_("Please provide an email address."))
            return self._send_invitation(id_, email=email)
