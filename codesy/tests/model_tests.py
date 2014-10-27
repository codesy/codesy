from django.test import TestCase
from django.test.client import RequestFactory

import fudge

from ..base.models import EMAIL_URL, User, add_email_from_signup


VERIFIED_PRIMARY_EMAIL = "verified-primary@test.com"

GITHUB_DATA_WITH_VERIFIED_PRIMARY_EMAIL = [
    {u'verified': True,
     u'email': u'%s' % VERIFIED_PRIMARY_EMAIL,
     u'primary': True}
]


class SignUpReceiverTest(TestCase):
    def setUp(self):
        self.sociallogin = fudge.Fake().has_attr(token='12345')

    @fudge.patch('requests.get')
    def test_save_email_from_github_api(self, fake_get):
        params = {'access_token': self.sociallogin.token}
        (fake_get.expects_call()
                 .with_args(EMAIL_URL, params=params)
                 .returns_fake()
                 .expects('json')
                 .returns(
                     GITHUB_DATA_WITH_VERIFIED_PRIMARY_EMAIL))
        sender = User
        request = RequestFactory()
        user = fudge.Fake('User').has_attr(email=None).expects('save')
        kwargs = {'sociallogin': self.sociallogin}

        add_email_from_signup(sender, request, user, **kwargs)
        self.assertEquals(VERIFIED_PRIMARY_EMAIL, user.email)
