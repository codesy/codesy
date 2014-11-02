from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse
from django.test import TestCase
from model_mommy import mommy
import fudge

from codesy import base, serializers, views


class AuthViewTest(TestCase):
    def test_allauth_signup_disabled(self):
        resp = self.client.get(reverse("account_signup"))
        self.assertContains(resp, 'Sign Up Closed')


class UserViewSetTest(TestCase):
    def setUp(self):
        self.view = views.UserViewSet()

    def test_attrs(self):
        self.assertIsInstance(self.view, views.ModelViewSet)
        self.assertEqual(self.view.model, base.models.User)
        self.assertEqual(
            self.view.serializer_class, serializers.UserSerializer)

    def test_get_object(self):
        user = mommy.make(settings.AUTH_USER_MODEL)
        self.view.request = fudge.Fake().has_attr(user=user)

        obj = self.view.get_object()

        self.assertEqual(obj, user)


class HomeTest(TestCase):
    def setUp(self):
        self.view = views.Home()

    def test_attrs(self):
        self.assertIsInstance(self.view, views.TemplateView)
        self.assertEqual(self.view.template_name, 'home.html')

    @fudge.patch('codesy.views.TemplateView.get_context_data')
    @fudge.patch('codesy.views.Home.get_gravatar_url')
    def test_get_context_data(self, mock_get_context, mock_gravatar):
        mock_get_context.expects_call().returns({'super': 'context'})
        mock_gravatar.expects_call().returns('http://gravatar.com/stuff')

        context = self.view.get_context_data()

        self.assertEqual(
            context,
            {'super': 'context',
             'gravatar_url': 'http://gravatar.com/stuff'})

    def test_get_gravatar_url(self):
        user = mommy.make(settings.AUTH_USER_MODEL, email='fake@email.com')
        self.view.request = fudge.Fake().has_attr(user=user)

        url = self.view.get_gravatar_url()

        self.assertEqual(
            url,
            'http://www.gravatar.com/avatar/724f95667e2fbe903ee1b4cffcae3b25'
            '?s=40')

    def test_get_gravatar_url_anon_user(self):
        user = AnonymousUser()
        self.view.request = fudge.Fake().has_attr(user=user)

        url = self.view.get_gravatar_url()

        self.assertEqual(url, 'http://www.gravatar.com/avatar/?s=40')
