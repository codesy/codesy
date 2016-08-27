import fudge

from django.test import TestCase

from ..views import StripeHookView

from ..models import StripeEvent

from . import account_updated


class StripeHookTest(TestCase):

    def setUp(self):
        self.view = StripeHookView()
        self.valid_request = fudge.Fake().has_attr(body=account_updated)
        self.empty_request = fudge.Fake().has_attr(body='{}')

    def test_post_valid_event(self):
        self.view.request = self.valid_request
        self.view.post()
        event = StripeEvent.objects.all()[0]
        self.assertEqual(event.event_id, 'evt_00000000000000')

        # repeated event should not save
        self.view.post()
        events = StripeEvent.objects.all()
        self.assertEqual(events.count(), 1)

    def test_post_invalid_event(self):
        self.view.request = self.empty_request
        with self.assertRaises(KeyError):
            self.view.post()
