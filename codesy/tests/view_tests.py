from django.core.urlresolvers import reverse
from django.test import TestCase
import fudge

from codesy import views


class AuthViewTest(TestCase):
    def test_allauth_signup_disabled(self):
        resp = self.client.get(reverse("account_signup"))
        self.assertContains(resp, 'Sign Up Closed')


class HomeTest(TestCase):
    def setUp(self):
        self.view = views.Home()
        self.view.request = fudge.Fake()

    def test_attrs(self):
        self.assertIsInstance(self.view, views.TemplateView)
        self.assertEqual(self.view.template_name, 'home.html')

    @fudge.patch('codesy.views.TemplateView.get_context_data')
    def test_get_context_data(self, mock_get_context):
        mock_get_context.expects_call().returns({'super': 'context'})

        context = self.view.get_context_data()

        expected_keys = ['super', 'browser', 'cc_debug']
        for expected_key in expected_keys:
            self.assertIn(expected_key, context.keys())

    def test_get_browser(self):
        self.view.request.has_attr(META={
            'HTTP_USER_AGENT': 'Mozilla/5.0 '
            '(Macintosh; Intel Mac OS X 10.10; rv:37.0) '
            'Gecko/20100101 '
            'Firefox/37.0'
        })
        self.assertEquals('Firefox', self.view.get_browser()['name'])

        self.view.request.has_attr(META={
            'HTTP_USER_AGENT': 'Mozilla/5.0 '
            '(Macintosh; Intel Mac OS X 10_10_2) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/42.0.2300.2 '
            'Safari/537.36'
        })
        self.assertEquals('Chrome', self.view.get_browser()['name'])
