import fudge

from django.conf import settings
from django.test import TestCase

from model_mommy import mommy


class NotifyMatchersReceiverTest(TestCase):
    def setUp(self):
        """
        Set up the following market of Bids for a single bug:
            user1: ask 50,  offer 0
            user2: ask 100, offer 10
            user3: ask 0,   offer 30
        """
        self.url = 'http://github.com/codesy/codesy/issues/37'
        self.bid1 = mommy.make('auctions.Bid', user__email='user1@test.com',
                               ask=50, offer=0, url=self.url)
        self.bid2 = mommy.make('auctions.Bid', user__email='user2@test.com',
                               ask=100, offer=10, url=self.url)
        self.bid3 = mommy.make('auctions.Bid', user__email='user3@test.com',
                               ask=0, offer=30, url=self.url)

    def _add_url(self, string):
        return string.format(url=self.url)

    @fudge.patch('auctions.models.send_mail')
    def test_send_mail_to_matching_askers(self, mock_send_mail):
        user = mommy.make(settings.AUTH_USER_MODEL)

        mock_send_mail.expects_call().with_args(
            self._add_url('[codesy] Your ask for 50 for {url} has been met'),
            self._add_url('Bidders have met your asking price for {url}.'),
            settings.DEFAULT_FROM_EMAIL,
            ['user1@test.com']
        )
        mock_send_mail.next_call().with_args(
            self._add_url('[codesy] Your ask for 100 for {url} has been met'),
            self._add_url('Bidders have met your asking price for {url}.'),
            settings.DEFAULT_FROM_EMAIL,
            ['user2@test.com']
        )

        offer_bid = mommy.prepare(
            'auctions.Bid', offer=100, user=user, ask=1000, url=self.url)
        offer_bid.save()

    @fudge.patch('auctions.models.send_mail')
    def test_only_send_mail_to_unsent_matching_askers(self, mock_send_mail):
        user = mommy.make(settings.AUTH_USER_MODEL)
        self.bid1.ask_match_sent = True
        self.bid1.save()

        mock_send_mail.expects_call().with_args(
            self._add_url('[codesy] Your ask for 100 for {url} has been met'),
            self._add_url('Bidders have met your asking price for {url}.'),
            settings.DEFAULT_FROM_EMAIL,
            ['user2@test.com']
        )

        offer_bid = mommy.prepare(
            'auctions.Bid', offer=100, user=user, ask=1000, url=self.url)
        offer_bid.save()
