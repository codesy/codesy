import fudge

from django.conf import settings
from django.test import TestCase

from model_mommy import mommy

from ..models import Issue, Bid, Claim, Vote
from ..views import BidStatusView, ClaimStatusView
from ..views import BidList, ClaimList, VoteList


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
                             .has_attr(GET={'url': self.url})
                             .has_attr(user=self.user1))
        context = self.view.get_context_data()
        self.assertEqual(bid, context['bid'])


class ClaimStatusTestCase(TestCase):
    def setUp(self):
        self.view = ClaimStatusView()
        self.url = 'http://github.com/codesy/codesy/issues/37'
        self.issue = mommy.make(Issue, url=self.url)
        self.user1 = mommy.make(settings.AUTH_USER_MODEL,
                                email='user1@test.com')
        self.user2 = mommy.make(settings.AUTH_USER_MODEL,
                                email='user1@test.com')

        self.claim = mommy.make(Claim, user=self.user1, issue=self.issue)

    def payout_post(self, user):
        self.view.request = (fudge.Fake()
                             .has_attr(user=user))
        self.view.kwargs = {'pk': self.claim.id}
        response = self.view.post(self.view.request)
        self.assertTrue(response)

    def test_get_by_id_returns_context(self):
        self.view.request = (fudge.Fake()
                             .has_attr(user=self.user1))
        self.view.kwargs = {'pk': self.claim.id}
        context = self.view.get_context_data()
        self.assertEqual(self.claim, context['claim'])

    def test_get_by_non_claimaint_returns_context(self):
        self.view.request = (fudge.Fake()
                             .has_attr(user=self.user2))
        self.view.kwargs = {'pk': self.claim.id}
        context = self.view.get_context_data()
        self.assertEqual(self.claim, context['claim'])

    @fudge.patch('auctions.models.Claim.payout_request')
    @fudge.patch('auctions.views.messages')
    def test_post_success_by_claimaint(self, mock_paypal, mock_messages):
        mock_paypal.is_callable().returns(True)
        mock_messages.expects('success')
        self.payout_post(self.user1)

    @fudge.patch('auctions.models.Claim.payout_request')
    @fudge.patch('auctions.views.messages')
    def test_post_fail_by_claimaint(self, mock_paypal, mock_messages):
        mock_paypal.is_callable().returns(False)
        mock_messages.expects('error')
        self.payout_post(self.user1)

    @fudge.patch('auctions.models.Claim.payout_request')
    @fudge.patch('auctions.views.messages')
    def test_post_exception_by_claimaint(self, mock_paypal, mock_messages):
        mock_paypal.is_callable().raises(Exception('Paypal error'))
        mock_messages.expects('error')
        self.payout_post(self.user1)

    @fudge.patch('auctions.views.messages')
    def test_post_fail_by_other_user(self, mock_messages):
        mock_messages.expects('error')
        self.payout_post(self.user2)


class BidListViewTest(TestCase):
    def setUp(self):
        self.view = BidList()
        self.url = 'http://github.com/codesy/codesy/issues/37'
        self.issue = mommy.make(Issue, url=self.url)
        self.user1 = mommy.make(settings.AUTH_USER_MODEL,
                                email='user1@test.com')
        self.user2 = mommy.make(settings.AUTH_USER_MODEL,
                                email='user2@test.com')

    def test_bid_list(self):
        bid = mommy.make(Bid, user=self.user1, url=self.url, issue=self.issue)
        self.view.request = (fudge.Fake()
                             .has_attr(user=self.user1))
        context = self.view.get_context_data()
        self.assertEqual(bid, context['bids'][0])

        self.view.request = (fudge.Fake()
                             .has_attr(user=self.user2))
        context = self.view.get_context_data()
        self.assertEqual(0, len(context['bids']))


class ClaimListViewTest(TestCase):
    def setUp(self):
        self.view = ClaimList()
        self.url = 'http://github.com/codesy/codesy/issues/37'
        self.issue = mommy.make(Issue, url=self.url)
        self.user1 = mommy.make(settings.AUTH_USER_MODEL,
                                email='user1@test.com')
        self.user2 = mommy.make(settings.AUTH_USER_MODEL,
                                email='user2@test.com')
        self.claim = mommy.make(Claim, user=self.user1, issue=self.issue)

    def test_claim_list(self):
        self.view.request = (fudge.Fake()
                             .has_attr(user=self.user1))
        context = self.view.get_context_data()
        self.assertEqual(self.claim, context['claims'][0])

        self.view.request = (fudge.Fake()
                             .has_attr(user=self.user2))
        context = self.view.get_context_data()
        self.assertEqual(0, len(context['claims']))


class VoteListViewTest(TestCase):
    def setUp(self):
        self.view = VoteList()
        self.url = 'http://github.com/codesy/codesy/issues/37'
        self.issue = mommy.make(Issue, url=self.url)
        self.user1 = mommy.make(settings.AUTH_USER_MODEL,
                                email='user1@test.com')
        self.user2 = mommy.make(settings.AUTH_USER_MODEL,
                                email='user2@test.com')
        self.claim = mommy.make(Claim, user=self.user1, issue=self.issue)

    def test_vote_list(self):
        vote = mommy.make(Vote, user=self.user1,
                          claim=self.claim, approved=True)
        self.view.request = (fudge.Fake()
                             .has_attr(user=self.user1))
        context = self.view.get_context_data()
        self.assertEqual(vote, context['votes'][0])
        self.view.request = (fudge.Fake()
                             .has_attr(user=self.user2))
        context = self.view.get_context_data()
        self.assertEqual(0, len(context['votes']))
        vote2 = mommy.make(Vote, user=self.user2,
                           claim=self.claim, approved=False)
        context = self.view.get_context_data()
        self.assertEqual(1, len(context['votes']))
        self.assertEqual(vote2, context['votes'][0])
        self.assertEqual(self.user2, context['votes'][0].user)
