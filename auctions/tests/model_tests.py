from datetime import datetime, timedelta
import time

import fudge
from fudge.inspector import arg

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.db import IntegrityError

from model_mommy import mommy

from ..models import Bid, Claim, Issue, Vote


class MarketTestCase(TestCase):
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


class BidTests(MarketTestCase):
    def test_ask_met(self):
        self.assertFalse(self.bid1.ask_met())
        mommy.make(Bid, ask=0, offer=10, url=self.url)
        self.assertTrue(self.bid1.ask_met())

    def test_ask_met_doesnt_include_bidder(self):
        self.assertFalse(self.bid1.ask_met())
        self.bid1.offer = 50
        self.bid1.save()
        self.assertFalse(self.bid1.ask_met())

    def test_save_assigns_issue_for_existing_url(self):
        self.bid1 = Bid.objects.get(pk=self.bid1.id)
        existing_issue = self.bid1.issue
        new_bid = mommy.make(Bid, ask=200, offer=5, url=existing_issue.url)
        new_bid = Bid.objects.get(pk=new_bid.id)
        self.assertIsNotNone(new_bid.issue)
        issues = Issue.objects.all()
        self.assertEquals(1, len(issues))
        issue = issues[0]
        self.assertEquals(self.url, issue.url)

    def test_save_creates_issue_for_new_url(self):
        url = 'https://github.com/codesy/codesy/issues/165'
        mommy.make(Bid, ask=200, offer=5, url=url)
        issues = Issue.objects.all()
        self.assertEquals(2, len(issues))
        issue = Issue.objects.get(url=url)
        self.assertEquals(url, issue.url)

    def test_save_updates_datetimes(self):
        test_bid = mommy.make(Bid)
        test_bid = Bid.objects.get(pk=test_bid.pk)
        test_bid_created = test_bid.created
        self.assertTrue(
            datetime.now() >= test_bid_created.replace(tzinfo=None),
            "Bid.created should be auto-populated."
        )
        time.sleep(1)
        test_bid.ask = 100
        test_bid.offer = 10
        test_bid.save()
        self.assertEqual(test_bid_created, test_bid.created,
                         "Bid.created should stay the same after an update.")
        test_bid_modified = test_bid.modified
        self.assertTrue(test_bid_modified >= test_bid_created,
                        "Bid.modified should be auto-populated on update.")
        self.assertTrue(
            datetime.now() >= test_bid_modified.replace(tzinfo=None),
            "Bid.modified should be auto-populated."
        )


class NotifyMatchersReceiverTest(MarketTestCase):

    @fudge.patch('auctions.models.send_mail')
    def test_dont_email_self_when_offering_more_than_ask(self, mock_send_mail):
        mock_send_mail.is_callable().times_called(0)
        user = mommy.make(settings.AUTH_USER_MODEL)
        url = 'https://github.com/codesy/codesy/issues/149'
        offer_bid = mommy.prepare(
            Bid, user=user, url=url, offer=100, ask=10
        )
        offer_bid.save()

    @fudge.patch('auctions.models.send_mail')
    def test_send_mail_to_matching_askers(self, mock_send_mail):
        user = mommy.make(settings.AUTH_USER_MODEL)

        mock_send_mail.expects_call().with_args(
            self._add_url('[codesy] Your ask for 50 for {url} has been met'),
            arg.any(),
            arg.any(),
            ['user1@test.com']
        )
        mock_send_mail.next_call().with_args(
            self._add_url('[codesy] Your ask for 100 for {url} has been met'),
            arg.any(),
            arg.any(),
            ['user2@test.com']
        )

        offer_bid = mommy.prepare(
            Bid, offer=100, user=user, ask=1000, url=self.url
        )
        offer_bid.save()

    @fudge.patch('auctions.models.send_mail')
    def test_only_send_mail_to_unsent_matching_askers(self, mock_send_mail):
        user = mommy.make(settings.AUTH_USER_MODEL)
        self.bid1.ask_match_sent = datetime.now()
        self.bid1.save()

        mock_send_mail.expects_call().with_args(
            self._add_url('[codesy] Your ask for 100 for {url} has been met'),
            arg.any(),
            arg.any(),
            ['user2@test.com']
        )

        offer_bid = mommy.prepare(
            Bid, offer=100, user=user, ask=1000, url=self.url
        )
        offer_bid.save()

    @fudge.patch('auctions.models.send_mail')
    def test_mail_contains_text_for_claiming_via_url(self, mock_send_mail):
        user = mommy.make(settings.AUTH_USER_MODEL)
        self.bid1.ask_match_sent = datetime.now()
        self.bid1.save()

        mock_send_mail.expects_call().with_args(
            arg.any(),
            arg.contains("visiting the issue url:\n"),
            arg.any(),
            ['user2@test.com']
        )

        mommy.make(
            Bid, offer=100, user=user, ask=1000, url=self.url
        )


class ClaimTest(TestCase):
    def test_default_values(self):
        test_claim = mommy.make(Claim)
        self.assertEqual('Pending', test_claim.status)

    # HACK: ? do we really need to test whether I typed correctly?
    def test_get_absolute_url_returns_claim_status(self):
        test_claim = mommy.make(Claim)
        test_claim = Claim.objects.get(pk=test_claim.pk)
        self.assertTrue(
            reverse('custom-urls:claim-status',
                    kwargs={'pk': test_claim.id})
            in test_claim.get_absolute_url()
        )

    def test_expires_is_30_days_after_create(self):
        test_claim = mommy.make(Claim)
        test_claim = Claim.objects.get(pk=test_claim.pk)
        self.assertEqual(test_claim.expires,
                         test_claim.created + timedelta(days=30))

    def test_save_updates_datetimes(self):
        test_claim = mommy.make(Claim)
        test_claim = Claim.objects.get(pk=test_claim.pk)
        test_claim_created = test_claim.created
        self.assertTrue(
            datetime.now() >= test_claim_created.replace(tzinfo=None),
            "Claim.created should be auto-populated."
        )
        time.sleep(1)
        test_claim.evidence = 'https://test.com/123'
        test_claim.save()
        self.assertEqual(test_claim_created, test_claim.created,
                         "Claim.created should stay the same after an update.")
        test_claim_modified = test_claim.modified
        self.assertTrue(test_claim_modified >= test_claim_created,
                        "Claim.modified should be auto-populated on update.")
        self.assertTrue(
            datetime.now() >= test_claim_modified.replace(tzinfo=None),
            "Claim.modified should be auto-populated."
        )


class NotifyMatchingOfferersTest(MarketTestCase):
    def setUp(self):
        """
        Add a final bid and a user2 claim to the MarketTestCase,
        so the final market for the bug is now:
            url: http://github.com/codesy/codesy/issues/37
            user1: ask 50,  offer 0  (ask is met)
            user2: ask 100, offer 10
            user3: ask 0,   offer 30
            user4: ask 200, offer 10
        And user1 is making the claim
        """
        super(NotifyMatchingOfferersTest, self).setUp()
        self.user4 = mommy.make(settings.AUTH_USER_MODEL,
                                email='user4@test.com')
        self.bid4 = mommy.make(Bid, user=self.user4,
                               ask=200, offer=10, url=self.url)
        self.evidence = ('https://github.com/codesy/codesy/commit/'
                         '4f1bcd014ec735918bebd1c386e2f99a7f83ff64')

    @fudge.patch('auctions.models.send_mail')
    def test_send_email_to_other_offerers_when_claim_is_made(self,
                                                             mock_send_mail):
        # Should be called 3 times: for user2, user3, and user4
        mock_send_mail.is_callable().times_called(3)
        mommy.make(
            Claim,
            user=self.user1,
            issue=self.issue,
            evidence=self.evidence,
            created=datetime.now()
        )

    @fudge.patch('auctions.models.send_mail')
    def test_dont_send_email_to_bidders_who_offered_0(self,
                                                      mock_send_mail):
        user5 = mommy.make(settings.AUTH_USER_MODEL,
                           email='user5@test.com')
        mommy.make(Bid, user=user5, ask=500, offer=0, url=self.url)

        # Should still be called just 3 times: for user2, user3, and user4
        mock_send_mail.is_callable().times_called(3)
        mommy.make(
            Claim,
            user=self.user1,
            issue=self.issue,
            evidence=self.evidence,
            created=datetime.now()
        )

    @fudge.patch('auctions.models.send_mail')
    def test_dont_send_email_on_saving_claim(self, mock_send_mail):
        mock_send_mail.is_callable().times_called(3)
        claim = mommy.make(
            Claim,
            user=self.user1,
            issue=self.issue,
            created=datetime.now()
        )
        claim.evidence = 'http://test.com/updated-evidence'
        claim.save()
        claim.status = 'Rejected'
        claim.save()


class VoteTest(TestCase):
    def setUp(self):
        self.user1 = mommy.make(settings.AUTH_USER_MODEL,
                                email='user1@test.com')
        self.user2 = mommy.make(settings.AUTH_USER_MODEL,
                                email='user2@test.com')
        self.user3 = mommy.make(settings.AUTH_USER_MODEL,
                                email='user3@test.com')
        url = 'http://test.com/bug/123'
        issue = mommy.make(Issue, url=url)

        mommy.make(Bid, user=self.user1, url=url, issue=issue, ask=50)
        mommy.make(Bid, user=self.user2, url=url, issue=issue, offer=50)
        mommy.make(Bid, user=self.user3, url=url, issue=issue, offer=50)
        self.claim = mommy.make(Claim, issue=issue, user=self.user1)

    def test_save_updates_datetimes(self):
        test_vote = mommy.make(Vote, approved=False)
        test_vote = Vote.objects.get(pk=test_vote.pk)
        test_vote_created = test_vote.created
        self.assertTrue(
            datetime.now() >= test_vote_created.replace(tzinfo=None),
            "Vote.created should be auto-populated."
        )
        time.sleep(1)
        test_vote.approved = True
        test_vote.save()
        self.assertEqual(test_vote_created, test_vote.created,
                         "Vote.created should stay the same after an update.")
        test_vote_modified = test_vote.modified
        self.assertTrue(test_vote_modified >= test_vote_created,
                        "Vote.modified should be auto-populated on update.")
        self.assertTrue(
            datetime.now() >= test_vote_modified.replace(tzinfo=None),
            "Vote.modified should be auto-populated."
        )

    def test_user_claim_unique(self):
        mommy.make(Vote, claim=self.claim, user=self.user1, approved=True)
        with self.assertRaises(IntegrityError):
            mommy.make(Vote, claim=self.claim, user=self.user1, approved=False)

    @fudge.patch('auctions.models.send_mail')
    def test_notify_claim_approved(self, mock_send_mail):
        mock_send_mail.expects_call()
        mommy.make(Vote, claim=self.claim, user=self.user2, approved=True)
        mommy.make(Vote, claim=self.claim, user=self.user3, approved=True)

    @fudge.patch('auctions.models.send_mail')
    def test_claimant_vote_not_counted(self, mock_send_mail):
        mock_send_mail.is_callable().times_called(0)
        mommy.make(Vote, claim=self.claim, user=self.user1, approved=True)
        mommy.make(Vote, claim=self.claim, user=self.user2, approved=True)

    @fudge.patch('auctions.models.send_mail')
    def test_no_votes_not_counted(self, mock_send_mail):
        mock_send_mail.is_callable().times_called(0)
        mommy.make(Vote, claim=self.claim, user=self.user2, approved=False)
        mommy.make(Vote, claim=self.claim, user=self.user3, approved=True)
