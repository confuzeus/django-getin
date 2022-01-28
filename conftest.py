from unittest.mock import MagicMock

import pytest
from django.contrib.admin import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.http import HttpRequest
from faker import Faker

from getin.admin import InvitationAdmin
from getin.models import Invitation

User = get_user_model()


@pytest.fixture
def fake():
    return Faker()


@pytest.fixture
def site(db) -> Site:
    site = Site.objects.first()

    if not site:
        site = Site.objects.create(name=fake.word(), domain=fake.domain_name())

    return site


@pytest.fixture
def invite_code():
    return Invitation.generate_code()


@pytest.fixture
def unsent_invitation(db):
    return Invitation.create()


@pytest.fixture
def sent_invitation(db, unsent_invitation):
    send_fn = MagicMock()
    unsent_invitation.send_invitation(send_fn)
    unsent_invitation.save()
    return unsent_invitation


@pytest.fixture
def consumed_invitation(db, sent_invitation, user):
    sent_invitation.consume(user)
    sent_invitation.save()
    return sent_invitation


@pytest.fixture
def user(db, fake):
    return User.objects.create(username=fake.user_name(), email=fake.ascii_email())


@pytest.fixture
def admin_user(db, fake):
    return User.objects.create(
        username=fake.user_name(), email=fake.ascii_email(), is_staff=True
    )


@pytest.fixture
def invitation_admin(db) -> InvitationAdmin:
    admin_site = AdminSite()
    return InvitationAdmin(model=Invitation, admin_site=admin_site)


@pytest.fixture
def admin_request(admin_user, rf) -> HttpRequest:
    request = rf.get("/")
    request.user = admin_user
    return request
