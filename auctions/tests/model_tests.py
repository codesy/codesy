from datetime import datetime, timedelta
import time
from decimal import Decimal

import fudge
from fudge.inspector import arg

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.db import IntegrityError
from django.db.models import Sum

from model_mommy import mommy

from payments.models import StripeAccount
from ..models import Bid, Claim, Issue, Vote
from ..models import Offer, OfferFee, Payout, PayoutFee, PayoutCredit

from . import MarketWithBidsTestCase, MarketWithClaimTestCase


class IssueTest(MarketWithBidsTestCase):

    def test_unicode(self):
        self.issue.state = 'unknown'
        self.assertEqual(
            str(self.issue), u'%s (%s)' % (self.url, self.issue.state)
        )


class SignalTest(TestCase):

    def test_save_title(self):
        ModelsWithURL = ['Bid', 'Claim', 'Issue']
        for model_name in ModelsWithURL:
            model = mommy.make(model_name)
            retrieve_model = type(model).objects.get(pk=model.id)
            self.assertEqual(retrieve_model.title, 'Howdy Dammit')


class SimpleBidTest(TestCase):

    def test_no_charge_for_zero_offer(self):
        bid = mommy.make(Bid, ask=50)
        offers = Offer.objects.filter(bid=bid)
        self.assertEqual(len(offers), 0)


class BidTest(MarketWithBidsTestCase):

    def test_ask_met(self):
        self.assertFalse(self.bid1.ask_met())
        mommy.make(Bid, ask=0, offer=10, url=self.url)
        self.assertTrue(self.bid1.ask_met())

    def test_zero_ask_return_false(self):
        self.assertEqual(self.bid3.ask_met(), False)

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


class BidWithClaimsTest(MarketWithClaimTestCase):
    def setUp(self):
        super(BidWithClaimsTest, self).setUp()
        self.url2 = 'http://github.com/codesy/codesy/issues/38'
        self.issue2 = mommy.make(Issue, url=self.url2)
        self.new_bid = mommy.make(Bid, user=self.user2, ask=100, offer=5,
                                  url=self.url2, issue=self.issue2)

    def test_claim_for_user(self):
        self.assertEqual(self.claim, self.bid1.claim_for_user(self.user1))
        with self.assertRaises(Claim.DoesNotExist):
            self.bid1.claim_for_user(self.user2)

    def test_claims_for_other_users(self):
        user1_others_claims = self.bid1.claims_for_other_users(self.user1)
        self.assertEqual([], list(user1_others_claims))
        user2_others_claims = self.bid1.claims_for_other_users(self.user2)
        self.assertEqual(1, len(list(user2_others_claims)))
        self.assertEqual(self.user1, user2_others_claims[0].user)

    def test_actionable_claims_includes_own_claim(self):
        self.assertEqual(self.claim,
                         self.bid1.actionable_claims(self.user1)['own_claim'])
        self.assertEqual(None,
                         self.bid1.actionable_claims(self.user2)['own_claim'])

    def test_actionable_claims_includes_other_claims(self):
        self.assertIn(self.claim,
                      self.bid1.actionable_claims(self.user2)['other_claims'])
        self.assertNotIn(
            self.claim,
            self.bid1.actionable_claims(self.user1)['other_claims']
        )

    def test_all_users_can_bid_when_theres_no_claim(self):
        self.assertTrue(self.new_bid.is_biddable_by(self.user1))
        self.assertTrue(self.new_bid.is_biddable_by(self.user2))
        self.assertTrue(self.new_bid.is_biddable_by(self.user3))

    def test_no_users_can_bid_when_theres_a_claim(self):
        self.assertFalse(self.bid1.is_biddable_by(self.user1))
        self.assertFalse(self.bid1.is_biddable_by(self.user2))
        self.assertFalse(self.bid1.is_biddable_by(self.user3))

    def test_user_cannot_bid_when_their_ask_has_been_met(self):
        self.assertFalse(self.bid1.is_biddable_by(self.user1))

    def test_other_users_can_still_bid_when_someones_ask_has_been_met(self):
        self.assertTrue(self.new_bid.is_biddable_by(self.user2))


class NotifyMatchersReceiverTest(MarketWithBidsTestCase):

    @fudge.patch('auctions.models.send_mail')
    def test_dont_email_self_when_offering_more_than_ask(self, mock_send_mail):
        mock_send_mail.is_callable().times_called(0)
        user = mommy.make(settings.AUTH_USER_MODEL)
        url = 'https://github.com/codesy/codesy/issues/149'
        offer_bid = mommy.make(
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

        offer_bid = mommy.make(
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

        offer_bid = mommy.make(
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


class ClaimTest(MarketWithClaimTestCase):
    def test_default_values(self):
        test_claim = mommy.make(Claim)
        self.assertEqual('Submitted', test_claim.status)

    # HACK: ? do we really need to test whether I typed correctly?
    def test_get_absolute_url_returns_claim_status(self):
        test_claim = mommy.make(Claim)
        test_claim = Claim.objects.get(pk=test_claim.pk)
        self.assertTrue(
            reverse('claim-status',
                    kwargs={'pk': test_claim.id})
            in test_claim.get_absolute_url()
        )

    def test_vote_changes_status_to_pending(self):
        mommy.make(Vote, user=self.user2, claim=self.claim, approved=True)
        self.claim = Claim.objects.get(id=self.claim.id)
        self.assertEqual('Pending', self.claim.status)

    def test_unamimous_approvals_changes_status_to_approved(self):
        mommy.make(Vote, user=self.user2, claim=self.claim, approved=True)
        mommy.make(Vote, user=self.user3, claim=self.claim, approved=True)
        self.claim = Claim.objects.get(id=self.claim.id)
        self.assertEqual('Approved', self.claim.status)

    def test_unamimous_rejections_changes_status_to_rejected(self):
        mommy.make(Vote, user=self.user2, claim=self.claim, approved=False)
        mommy.make(Vote, user=self.user3, claim=self.claim, approved=False)
        self.claim = Claim.objects.get(id=self.claim.id)
        self.assertEqual('Rejected', self.claim.status)

    def test_majority_rejections_changes_status_to_rejected(self):
        mommy.make(Vote, user=self.user2, claim=self.claim, approved=True)
        mommy.make(Vote, user=self.user3, claim=self.claim, approved=False)
        self.claim = Claim.objects.get(id=self.claim.id)
        self.assertEqual('Rejected', self.claim.status)

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

    def test_needs_from_user_who_already_voted_returns_false(self):
        mommy.make(Vote, user=self.user2, claim=self.claim, approved=True)
        self.assertFalse(self.claim.needs_vote_from_user(self.user2))

    def test_needs_from_user_with_no_bid_returns_false(self):
        user4 = mommy.make(settings.AUTH_USER_MODEL)
        self.assertFalse(self.claim.needs_vote_from_user(user4))

    def test_needs_from_user_with_bid_who_hasnt_voted_returns_true(self):
        self.assertTrue(self.claim.needs_vote_from_user(self.user3))


class NotifyMatchingOfferersTest(MarketWithBidsTestCase):
    def setUp(self):
        """
        Add a final bid and a user2 claim to the MarketWithBidsTestCase,
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

    def test_unicode(self):
        vote = mommy.make(Vote, approved=True)
        self.assertEqual(
            str(vote), 'Vote for %s by (%s): %s' %
            (vote.claim, vote.user, vote.approved)
        )

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


class OfferTest(TestCase):

    def setUp(self):
        self.user1 = mommy.make(settings.AUTH_USER_MODEL,
                                email='user1@test.com')
        self.url = 'http://test.com/bug/123'
        self.issue = mommy.make(Issue, url=self.url)
        self.bid = mommy.make(
            Bid, user=self.user1,
            url=self.url, issue=self.issue, offer=50)
        offer = self.bid.make_offer(50)
        offer.request()

    def test_key_created(self):
        offer = mommy.make(Offer, bid=self.bid)
        self.assertIsNotNone(offer.transaction_key)

    def test_bid_fees(self):
        offer = Offer.objects.get(bid=self.bid)
        self.assertEqual(offer.amount, 50)
        fees = OfferFee.objects.filter(offer=offer)
        self.assertEqual(len(fees), 2)
        self.assertEqual(len(fees), len(offer.fees()))
        sum_fees = fees.aggregate(Sum('amount'))['amount__sum']
        offer_with_fees = offer.amount + sum_fees
        self.assertEqual(offer_with_fees, offer.charge_amount)

    def test_new_offer(self):
        self.assertEqual(self.bid.offer, 50)
        offer = self.bid.make_offer(60)
        self.assertEqual(offer.amount, 10)
        offer.request()
        offers = Offer.objects.filter(bid=self.bid)
        self.assertEqual(len(offers), 2)
        self.assertEqual(len(self.bid.offers()), 2)
        sum_offers = offers.aggregate(Sum('amount'))['amount__sum']
        self.assertEqual(sum_offers, 60)

    def test_offer_fee_calculatons(self):
        AMOUNTS = [333, 22, 357, 1000, 50, 999, 1, ]
        for amount in AMOUNTS:
            new_bid = mommy.make(Bid, offer=amount)
            new_bid.make_offer(amount)
            offer = Offer.objects.get(bid=new_bid)
            fees = OfferFee.objects.filter(offer=offer)
            self.assertEqual(offer.request(), True)
            sum_fees = fees.aggregate(Sum('amount'))['amount__sum']
            self.assertEqual(offer.charge_amount - sum_fees, amount)


class PayoutTest(TestCase):

    def setUp(self):
        self.user1 = mommy.make(settings.AUTH_USER_MODEL,
                                email='user1@test.com')
        self.user2 = mommy.make(settings.AUTH_USER_MODEL,
                                email='user2@test.com')
        self.url = 'http://test.com/bug/123'
        self.issue = mommy.make(Issue, url=self.url)

        self.bid1 = mommy.make(
            Bid, user=self.user1,
            url=self.url, issue=self.issue, ask=50)

        self.bid2 = mommy.make(
            Bid, user=self.user2,
            url=self.url, issue=self.issue, offer=50)

    def test_payouts_property(self):
        claim = mommy.make(Claim)
        mommy.make(Payout, claim=claim)
        mommy.make(Payout, claim=claim)
        mommy.make(Payout, claim=claim)
        payouts = Payout.objects.all()
        self.assertEqual(len(claim.payouts.all()), len(payouts))

    def test_payout_request(self):
        claim = mommy.make(Claim, user=self.user1, issue=self.issue)
        account = mommy.make(StripeAccount, user=self.user1)
        self.assertEqual(account, self.user1.account())
        api_request = claim.payout_request()
        if api_request:
            self.assertEqual(claim.status, 'Paid')
            self.assertFalse(claim.payout_request())
        payouts = claim.payouts.all()
        payout = payouts[0]
        self.assertTrue(payout.api_success)
        self.assertEqual(len(payouts), 1)
        fees = PayoutFee.objects.filter(payout=payout)
        self.assertEqual(len(fees), 2)
        self.assertEqual(len(payout.fees()), len(fees))
        sum_fees = fees.aggregate(Sum('amount'))['amount__sum']
        self.assertEqual(sum_fees + payout.charge_amount, self.bid1.ask)

    def test_payout_fee_calculations(self):
        AMOUNTS = [333, 22, 357, 1000, 50, 999, 1, ]
        for amount in AMOUNTS:
            payout = mommy.make(Payout, amount=amount)
            mommy.make(StripeAccount, user=payout.user)
            payout.request()
            fees = PayoutFee.objects.filter(payout=payout)
            sum_fees = fees.aggregate(Sum('amount'))['amount__sum']
            self.assertEqual(sum_fees + payout.charge_amount, amount)

    def test_payout_refund(self):
        """
        A user getting paid for a claim should also get back any offers
        they made on the issue.
        """
        self.bid1.make_offer(10)
        self.bid1.save()
        mommy.make(Bid, user=self.user1, offer=50)
        mommy.make(StripeAccount, user=self.user1)

        claim = mommy.make(Claim, user=self.user1, issue=self.issue)
        api_request = claim.payout_request()
        if api_request:
            self.assertEqual(claim.status, 'Paid')
            self.assertFalse(claim.payout_request())
        payouts = claim.payouts.all()
        payout = payouts[0]
        self.assertTrue(payout.api_success)
        self.assertEqual(len(payouts), 1)

        refund = PayoutCredit.objects.filter(payout=payout)
        self.assertEqual(len(refund), 1)
        self.assertEqual(len(payout.credits()), len(refund))
        self.assertEqual(refund[0].amount, 10)
        self.assertEqual(payout.charge_amount, Decimal('58.20'))
