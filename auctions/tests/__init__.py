from model_mommy import mommy

from django.conf import settings
from django.test import TestCase

from ..models import Bid, Claim, Issue

import fudge


def setUpPackage(self):

    mock_get = fudge.Fake().is_callable().returns(
        fudge.Fake().has_attr(text='<title>Howdy Dammit</title>')
    )

    self.patch_request = fudge.patch_object(
        'auctions.models.requests', 'get', mock_get
    )

    mock_create = fudge.Fake().has_attr(id='dammit')

    mock_stripe = (
        fudge.Fake().provides('create').returns(mock_create)
    )

    self.patch_stripe = fudge.patch_object(
        'auctions.models.stripe', 'Charge', mock_stripe)

    fake_items = [fudge.Fake().has_attr(
        transaction_status='SUCCESS',
        payout_item_id='Howdy'),
    ]

    mock_paypal = (
        fudge.Fake().is_callable().returns(
            fudge.Fake().provides('create').returns(True)
            .has_attr(items=fake_items)
        )
    )

    self.patch_paypal = fudge.patch_object(
        'auctions.models', 'PaypalPayout', mock_paypal
    )


def tearDownPackage(self):
    self.patch_request.restore()
    self.patch_stripe.restore()
    self.patch_paypal.restore()


class MarketWithBidsTestCase(TestCase):
    def setUp(self):
        """
        Set up the following market of Bids for a single bug:
            url: http://github.com/codesy/codesy/issues/37
            user1: ask 50,  offer 0
            user2: ask 100, offer 10
            user3: ask 0,   offer 30
        """
        self.url = 'http://github.com/codesy/codesy/issues/37'
        self.issue = mommy.make(Issue, url=self.url)
        self.user1 = mommy.make(settings.AUTH_USER_MODEL,
                                email='user1@test.com')
        self.user2 = mommy.make(settings.AUTH_USER_MODEL,
                                email='user2@test.com')
        self.user3 = mommy.make(settings.AUTH_USER_MODEL,
                                email='user3@test.com')
        self.bid1 = mommy.make(Bid, user=self.user1,
                               ask=50, offer=0, url=self.url)
        self.bid2 = mommy.make(Bid, user=self.user2,
                               ask=100, offer=10, url=self.url)
        self.bid3 = mommy.make(Bid, user=self.user3,
                               ask=0, offer=30, url=self.url)

    def _add_url(self, string):
        return string.format(url=self.url)


class MarketWithClaimTestCase(TestCase):
    def setUp(self):
        """
        Set up the following claim senarios
            user1: asks 50
            user2: offers 25
            user3: offers 25
        """
        self.url = 'http://github.com/codesy/codesy/issues/37'
        self.issue = mommy.make(Issue, url=self.url)

        self.user1 = mommy.make(settings.AUTH_USER_MODEL,
                                email='user1@test.com')
        self.user2 = mommy.make(settings.AUTH_USER_MODEL,
                                email='user2@test.com')
        self.user3 = mommy.make(settings.AUTH_USER_MODEL,
                                email='user3@test.com')
        self.bid1 = mommy.make(Bid, user=self.user1,
                               ask=50, offer=0, url=self.url)
        self.bid2 = mommy.make(Bid, user=self.user2,
                               ask=0, offer=25, url=self.url)
        self.bid3 = mommy.make(Bid, user=self.user3,
                               ask=0, offer=25, url=self.url)
        self.claim = mommy.make(Claim, user=self.user1, issue=self.issue)
