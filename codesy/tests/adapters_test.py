import fudge

from django.forms import ValidationError

from django.test import TestCase
from django.test.client import RequestFactory

from codesy.adapters import CodesyAccountAdapter, CodesySocialAccountAdapter


class AdaptersTest(TestCase):
    """
    Verify our adapters are wired correctly.
    """
    def setUp(self):
        self.csaa = CodesySocialAccountAdapter()
        self.request = RequestFactory()
        self.sociallogin = fudge.Fake()

    def test_account_adapter_disabled(self):
        caa = CodesyAccountAdapter()
        self.assertEquals(False, caa.is_open_for_signup(self.request))

    def test_social_adapter_enabled(self):
        self.assertEquals(True, self.csaa.is_open_for_signup(self.request,
                                                             self.sociallogin))

    def test_social_adapter_prohibits_disconnecting_last_account(self):
        account = fudge.Fake()
        account2 = fudge.Fake()
        single_account_list = [account, ]
        multi_account_list = [account, account2]
        self.csaa.validate_disconnect(account, multi_account_list)

        with self.assertRaises(ValidationError):
            self.csaa.validate_disconnect(account, single_account_list)
