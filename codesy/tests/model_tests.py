from django.test import TestCase
from django.test.client import RequestFactory

from allauth.socialaccount.models import SocialAccount

import fudge
from model_mommy import mommy


from ..base.models import EMAIL_URL, User, add_email_from_signup


VERIFIED_PRIMARY_EMAIL = "verified+primary@test.com"
VERIFIED_EMAIL = "verified@test.com"
UNVERIFIED_EMAIL = "unverified@test.com"

GITHUB_DATA_WITH_VERIFIED_PRIMARY_EMAIL = [
    {u'verified': True,
     u'email': u'%s' % VERIFIED_PRIMARY_EMAIL,
     u'primary': True}
]
GITHUB_DATA_WITH_VERIFIED_EMAIL = [
    {u'verified': True,
     u'email': u'%s' % VERIFIED_EMAIL,
     u'primary': False}
]
GITHUB_DATA_WITH_UNVERIFIED_EMAIL = [
    {u'verified': False,
     u'email': u'%s' % UNVERIFIED_EMAIL,
     u'primary': False}
]
GITHUB_DATA_WITH_MANY_EMAILS = (GITHUB_DATA_WITH_UNVERIFIED_EMAIL +
                                GITHUB_DATA_WITH_VERIFIED_PRIMARY_EMAIL +
                                GITHUB_DATA_WITH_VERIFIED_EMAIL)


class SignUpReceiverTest(TestCase):
    def setUp(self):
        self.sociallogin = fudge.Fake().has_attr(token='12345')
        self.params = {'access_token': self.sociallogin.token}
        self.sender = User
        self.request = RequestFactory()
        self.user = (fudge.Fake('User')
                     .has_attr(email=None)
                     .expects('save'))
        self.kwargs = {'sociallogin': self.sociallogin}
        self.fake_get = fudge.Fake('requests.get')

    @fudge.patch('requests.get')
    def test_verified_primary_email_from_github_api(self, fake_get):
        (fake_get.expects_call()
                 .with_args(EMAIL_URL, params=self.params)
                 .returns_fake()
                 .expects('json')
                 .returns(
                     GITHUB_DATA_WITH_VERIFIED_PRIMARY_EMAIL))

        add_email_from_signup(self.sender,
                              self.request,
                              self.user,
                              **self.kwargs)
        self.assertEquals(VERIFIED_PRIMARY_EMAIL, self.user.email)

    @fudge.patch('requests.get')
    def test_verified_email_from_github_api(self, fake_get):
        (fake_get.expects_call()
                 .with_args(EMAIL_URL, params=self.params)
                 .returns_fake()
                 .expects('json')
                 .returns(
                     GITHUB_DATA_WITH_VERIFIED_EMAIL))

        add_email_from_signup(self.sender,
                              self.request,
                              self.user,
                              **self.kwargs)
        self.assertEquals(VERIFIED_EMAIL, self.user.email)

    @fudge.patch('requests.get')
    def test_unverified_email_from_github_api(self, fake_get):
        (fake_get.expects_call()
                 .with_args(EMAIL_URL, params=self.params)
                 .returns_fake()
                 .expects('json')
                 .returns(
                     GITHUB_DATA_WITH_UNVERIFIED_EMAIL))

        add_email_from_signup(self.sender,
                              self.request,
                              self.user,
                              **self.kwargs)
        self.assertEquals(None, self.user.email)

    @fudge.patch('requests.get')
    def test_many_emails_from_github_api(self, fake_get):
        (fake_get.expects_call()
                 .with_args(EMAIL_URL, params=self.params)
                 .returns_fake()
                 .expects('json')
                 .returns(
                     GITHUB_DATA_WITH_MANY_EMAILS))

        add_email_from_signup(self.sender,
                              self.request,
                              self.user,
                              **self.kwargs)
        self.assertEquals(VERIFIED_PRIMARY_EMAIL, self.user.email)

    @fudge.patch('stripe.Customer')
    def test_save_cc_token(self, mock_stripe):
        mock_stripe.provides('create').returns_fake().has_attr(id='dammit')
        user = mommy.make(User)
        user.stripe_account_token = "howdy"
        user.save()

    def test_get_gravatar_url(self):
        user = mommy.make(User, email='fake@email.com')
        mommy.make(SocialAccount, user=user, uid="12345")

        self.assertEqual(
            user.get_gravatar_url(),
            'https://avatars3.githubusercontent.com/u/12345?v=3&s=96'
        )
