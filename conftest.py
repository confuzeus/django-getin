import pytest
from faker import Faker
from django.contrib.sites.models import Site

from getin.models import Invitation


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
