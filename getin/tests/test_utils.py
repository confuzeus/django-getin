from unittest.mock import MagicMock, patch

import pytest

from getin.utils import email_invitation


def test_email_invitation_without_email():
    with pytest.raises(KeyError):
        email_invitation("")


@pytest.mark.django_db
def test_email_invitation_with_site(site, invite_code, fake):
    with patch("getin.utils.send_mail") as mock_send_mail:
        email_invitation(invite_code, email=fake.ascii_email())
        mock_send_mail.assert_called()


@pytest.mark.django_db
def test_email_invitation_without_site(invite_code, fake):
    with patch("getin.utils.send_mail") as mock_send_mail:
        with patch("getin.utils.Site") as MockSite:
            mock_objects = MagicMock()
            MockSite.DoesNotExist = Exception
            mock_objects.get.side_effect = MockSite.DoesNotExist()
            MockSite.objects = mock_objects

            email_invitation(invite_code, email=fake.ascii_email())
            mock_send_mail.assert_called()
