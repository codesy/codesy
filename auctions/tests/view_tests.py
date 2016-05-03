import fudge

from django.conf import settings
from django.test import TestCase

from model_mommy import mommy

from ..models import Issue, Bid
from ..views import BidStatusView


class BidStatusTestCase(TestCase):
    def setUp(self):
        self.view = BidStatusView()
        self.url = 'http://github.com/codesy/codesy/issues/37'
        self.issue = mommy.make(Issue, url=self.url)
        self.user1 = mommy.make(settings.AUTH_USER_MODEL,
                                email='user1@test.com')

    def test_get_by_url_returns_context(self):
        bid = mommy.make(Bid, user=self.user1, url=self.url, issue=self.issue)
        self.view.request = (fudge.Fake()
                             .has_attr(GET={'url':self.url})
                             .has_attr(user=self.user1))
        context = self.view.get_context_data()
        self.assertEqual(bid, context['bid'])

