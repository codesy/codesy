from decimal import Decimal

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
        self.bid1 = mommy.make(
            Bid, user=self.user1, url=self.url, issue=self.issue)

    def test_get_by_url_returns_context(self):
        self.view.request = (fudge.Fake()
                             .has_attr(GET={'url': self.url})
                             .has_attr(user=self.user1))
        context = self.view.get_context_data()
        self.assertEqual(self.bid1, context['bid'])

    def test_get_by_url_doesnt_create_bid(self):
        url = 'https://github.com/codesy/codesy/issues/419'
        self.view.request = (fudge.Fake()
                             .has_attr(GET={'url': url})
                             .has_attr(user=self.user1))
        context = self.view.get_context_data()
        self.assertIsNone(context['bid'])

    @fudge.patch('auctions.views.messages')
    def test_post_no_offer_value(self, mock_messages):
        mock_messages.is_a_stub()
        self.view.request = (fudge.Fake().has_attr(
            POST={
                'url': self.url,
                'ask': 4.20,
            })
            .has_attr(user=self.user1))
        self.view.post()
        retreive_bid = Bid.objects.get(pk=self.bid1.id)
        self.assertEqual(retreive_bid.ask, Decimal('4.20'))

    @fudge.patch('auctions.views.messages')
    def test_post_new_offer(self, mock_messages):
        mock_messages.is_a_stub()
        self.view.request = (fudge.Fake().has_attr(
            POST={
                'url': self.url,
                'ask': 0,
                'offer': 44.3,
            })
            .has_attr(user=self.user1))
        self.view.post()
        retreive_bid = Bid.objects.get(pk=self.bid1.id)
        self.assertEqual(retreive_bid.offer, Decimal('44.30'))

    def test_url_path_only(self):
        self.assertEqual(
            'https://github.com/codesy/codesy/issues/380',
            self.view._url_path_only(
                'https://github.com/codesy/codesy/issues/380#issue-163534117'
            )
        )
        self.assertEqual(
            'https://github.com/codesy/codesy/issues/380',
            self.view._url_path_only(
                'https://github.com/codesy/codesy/issues/380'
            )
        )

    @fudge.patch('auctions.views.messages')
    def test_post_no_ask_value(self, mock_messages):
        mock_messages.is_a_stub()
        self.view.request = (fudge.Fake().has_attr(
            POST={
                'url': self.url,
                'offer': 4.20,
            })
            .has_attr(user=self.user1))
        self.view.post()
        retreive_bid = Bid.objects.get(pk=self.bid1.id)
        self.assertEqual(retreive_bid.offer, Decimal('4.20'))

    @fudge.patch('auctions.views.messages')
    def test_post_new_ask_with_0_offer(self, mock_messages):
        mock_messages.is_a_stub()
        self.view.request = (fudge.Fake().has_attr(
            POST={
                'url': self.url,
                'ask': 5,
                'offer': 0,
            })
            .has_attr(user=self.user1))
        self.view.post()
        retreive_bid = Bid.objects.get(pk=self.bid1.id)
        self.assertEqual(retreive_bid.offer, 0)
        self.assertEqual(retreive_bid.ask, 5)

    @fudge.patch('auctions.views.messages')
    def test_post_new_ask_with_same_offer_only_asks(self, mock_messages):
        mock_messages.is_a_stub()
        self.view.request = (fudge.Fake().has_attr(
            POST={
                'url': self.url,
                'ask': 50,
                'offer': 5,
            })
            .has_attr(user=self.user1))
        self.view.post()
        retreive_bid = Bid.objects.get(pk=self.bid1.id)
        self.assertEqual(retreive_bid.offer, 5)
        self.assertEqual(retreive_bid.ask, 50)

    @fudge.patch('auctions.views.messages')
    def test_GET_POST_with_url_fragment(self, mock_messages):
        mock_messages.is_a_stub()
        url = 'https://github.com/codesy/codesy/issues/380'
        url_with_frag = '%s#issue-163534117' % url
        self.view.request = (fudge.Fake().has_attr(
            POST={
                'url': url_with_frag,
                'ask': 5,
                'offer': 0,
            })
            .has_attr(user=self.user1))
        self.view.post()

        self.view.request = (fudge.Fake()
                             .has_attr(GET={'url': url_with_frag})
                             .has_attr(user=self.user1))
        context = self.view.get_context_data()
        self.assertEqual(url, context['bid'].url)

        self.view.request = (fudge.Fake()
                             .has_attr(GET={'url': url})
                             .has_attr(user=self.user1))
        context = self.view.get_context_data()
        self.assertEqual(url, context['bid'].url)


class ClaimStatusTestCase(TestCase):
    def setUp(self):
        self.view = ClaimStatusView()
        self.url = 'http://github.com/codesy/codesy/issues/37'
        self.issue = mommy.make(Issue, url=self.url)
        self.user1 = mommy.make(
            settings.AUTH_USER_MODEL, email='user1@test.com'
        )
        self.bid1 = mommy.make(
            Bid, user=self.user1, url=self.url, issue=self.issue, offer=0
        )
        self.user2 = mommy.make(
            settings.AUTH_USER_MODEL, email='user2@test.com'
        )
        self.bid2 = mommy.make(
            Bid, user=self.user2, url=self.url, issue=self.issue, offer=10
        )
        self.user3 = mommy.make(
            settings.AUTH_USER_MODEL, email='user3@test.com'
        )

        self.claim = mommy.make(Claim, user=self.user1, issue=self.issue)

    def payout_post(self, user):
        self.view.request = (fudge.Fake()
                             .has_attr(user=user))
        self.view.kwargs = {'pk': self.claim.id}
        response = self.view.post(self.view.request)
        self.assertTrue(response)

    def test_get_by_id_returns_context(self):
        self.view.request = (fudge.Fake()
                             .has_attr(user=self.user1, path=""))
        self.view.kwargs = {'pk': self.claim.id}
        context = self.view.get_context_data()
        self.assertEqual(self.claim, context['claim'])

    def test_get_by_claimaint_returns_200_and_context(self):
        self.view.request = (fudge.Fake()
                             .has_attr(user=self.user1, path=""))
        self.view.kwargs = {'pk': self.claim.id}
        response = self.view.get(self.view.request)
        self.assertEqual(200, response.status_code)
        context = self.view.get_context_data()
        self.assertEqual(self.claim, context['claim'])

    def test_get_by_bidder_returns_200(self):
        self.view.request = (fudge.Fake()
                             .has_attr(user=self.user2, path=""))
        self.view.kwargs = {'pk': self.claim.id}
        response = self.view.get(self.view.request)
        self.assertEqual(200, response.status_code)
        context = self.view.get_context_data()
        self.assertEqual(self.claim, context['claim'])

    def test_get_by_non_bidding_user_returns_404(self):
        self.view.request = (fudge.Fake()
                             .has_attr(user=self.user3, path=""))
        self.view.kwargs = {'pk': self.claim.id}
        response = self.view.get(self.view.request)
        self.assertEqual(404, response.status_code)

    @fudge.patch('auctions.models.Claim.payout')
    @fudge.patch('auctions.views.messages')
    def test_post_success_by_claimaint(self, mock_paypal, mock_messages):
        mock_paypal.is_callable().returns(True)
        mock_messages.expects('success')
        self.payout_post(self.user1)

    @fudge.patch('auctions.models.Claim.payout')
    @fudge.patch('auctions.views.messages')
    def test_post_fail_by_claimaint(self, mock_paypal, mock_messages):
        mock_paypal.is_callable().returns(False)
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
