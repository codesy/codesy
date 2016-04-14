import uuid
import requests
import re
import HTMLParser
import stripe
import paypalrestsdk
from paypalrestsdk import Payout as PaypalPayout

from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver

from decimal import Decimal
from mailer import send_mail

stripe.api_key = settings.STRIPE_SECRET_KEY

# TODO: Find a prettier way to authenticate
paypalrestsdk.configure({"mode": settings.PAYPAL_MODE,
                         "client_id": settings.PAYPAL_CLIENT_ID,
                         "client_secret": settings.PAYPAL_CLIENT_SECRET,
                         })


def uuid_please():
    full_uuid = uuid.uuid4()
    # uuid is truncated because paypal must be <30
    return str(full_uuid)[:25]


class Bid(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    url = models.URLField()
    title = models.CharField(max_length=255, null=True, blank=True)
    issue = models.ForeignKey('Issue', null=True)
    ask = models.DecimalField(max_digits=6, decimal_places=2, blank=True,
                              default=0)
    ask_match_sent = models.DateTimeField(null=True, blank=True)
    offer = models.DecimalField(max_digits=6, decimal_places=2, blank=True,
                                default=0)
    created = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        unique_together = (("user", "url"),)

    def __unicode__(self):
        return u'%s bid on %s' % (self.user, self.url)

    def ask_met(self):
        if self.ask:
            other_bids = Bid.objects.filter(
                url=self.url
            ).exclude(
                user=self.user
            ).aggregate(
                Sum('offer')
            )
            return other_bids['offer__sum'] >= self.ask
        else:
            return False

    def offers(self):
        return Offer.objects.filter(bid=self)


@receiver(post_save, sender=Bid)
def get_payment_for_offer(sender, instance, **kwargs):
    if not instance.offer:
        return

    offer_amount = instance.offer
    user = instance.user
    offers = Offer.objects.filter(bid=instance)
    if offers:
        sum_offers = offers.aggregate(Sum('amount'))
        if offer_amount > sum_offers['amount__sum']:
            offer_amount = offer_amount - sum_offers['amount__sum']

# TODO: HANDLE CARD NOT YET REGISTERED

    stripe_pct = Decimal('0.029')
    stripe_transaction = Decimal('0.30')
    codesy_pct = Decimal('0.025')

    new_offer = Offer(
        user=user,
        amount=offer_amount,
        bid=instance,
    )
    new_offer.save()

    codesy_fee = OfferFee(
        offer=new_offer,
        fee_type='codesy',
        amount=new_offer.amount * codesy_pct
    )
    codesy_fee.save()

    stripe_charge = (
        (offer_amount + codesy_fee.amount + stripe_transaction)
        / (1 - stripe_pct)
    )

    stripe_fee = stripe_charge - (new_offer.amount + codesy_fee.amount)

    stripe_fee = OfferFee(
        offer=new_offer,
        fee_type='Stripe',
        amount=stripe_fee
    )
    stripe_fee.save()

    # TODO: removed with proper stripe mocking in tests
    new_offer.charge_amount = stripe_charge
    new_offer.save()

    try:
        charge = stripe.Charge.create(
            amount=int(stripe_charge * 100),
            currency="usd",
            customer=user.stripe_account_token,
            description="Offer for: " + instance.url,
            metadata={'id': new_offer.id}
        )
        if charge:
            new_offer.charge_amount = stripe_charge
            new_offer.confirmation = charge.id
            new_offer.save()
    except:
        pass


@receiver(post_save, sender=Bid)
def notify_matching_askers(sender, instance, **kwargs):
    # TODO: make a nicer HTML email template
    ASKER_NOTIFICATION_EMAIL_STRING = """
    Bidders have met your asking price for {url}.

    If you fix the issue, you may claim the payout by visiting the issue url:
    {url}
    """

    unnotified_asks = Bid.objects.filter(
        url=instance.url, ask_match_sent=None).exclude(ask__lte=0)

    for bid in unnotified_asks:
        if bid.ask_met():
            send_mail(
                "[codesy] Your ask for %(ask)d for %(url)s has been met" %
                (
                    {'ask': bid.ask, 'url': bid.url}
                ),
                ASKER_NOTIFICATION_EMAIL_STRING.format(url=bid.url),
                settings.DEFAULT_FROM_EMAIL,
                [bid.user.email]
            )
            # use .update to avoid recursive signal processing
            Bid.objects.filter(id=bid.id).update(ask_match_sent=datetime.now())


@receiver(post_save, sender=Bid)
def create_issue_for_bid(sender, instance, **kwargs):
    issue, created = Issue.objects.get_or_create(
        url=instance.url,
        defaults={'state': 'unknown', 'last_fetched': None}
    )
    # use .update to avoid recursive signal processing
    Bid.objects.filter(id=instance.id).update(issue=issue)


class Issue(models.Model):
    url = models.URLField(unique=True, db_index=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255)
    last_fetched = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'Issue for %s (%s)' % (self.url, self.state)


class Claim(models.Model):
    STATUS_CHOICES = (
        ('Submitted', 'Submitted'),
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Paid', 'Paid')
    )
    issue = models.ForeignKey('Issue')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    created = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(null=True, blank=True, auto_now=True)
    evidence = models.URLField(blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255,
                              choices=STATUS_CHOICES,
                              default='Submitted')

    class Meta:
        unique_together = (("user", "issue"),)

    def __unicode__(self):
        return u'%s claim on Issue %s (%s)' % (
            self.user, self.issue.id, self.status
        )

    def payouts(self):
        return Payout.objects.filter(claim=self).all()

    def votes_by_approval(self, approved):
        return (Vote.objects
                    .filter(claim=self, approved=approved)
                    .exclude(user=self.user))

    @property
    def num_approvals(self):
        return self.votes_by_approval(True).count()

    @property
    def num_rejections(self):
        return self.votes_by_approval(False).count()

    @property
    def num_votes(self):
        return Vote.objects.filter(claim=self).exclude(user=self.user)

    @property
    def offers(self):
        return (Bid.objects.filter(issue=self.issue)
                           .exclude(user=self.user)
                           .filter(offer__gt=0))

    @property
    def expires(self):
        return self.created + timedelta(days=30)

    def get_absolute_url(self):
        return reverse('custom-urls:claim-status', kwargs={'pk': self.id})

    def request_payout(self):
        if self.status == 'Paid':
            return False

        bid = Bid.objects.get(url=self.issue.url, user=self.user)

        codesy_payout = Payout(
            user=self.user,
            claim=self,
            amount=bid.ask,
        )
        codesy_payout.save()

        paypal_fee = PayoutFee(
            payout=codesy_payout,
            fee_type='PayPal',
            amount=Decimal('0.25')
        )
        paypal_fee.save()

        codesy_fee = PayoutFee(
            payout=codesy_payout,
            fee_type='codesy',
            amount=bid.ask * Decimal('0.025'),
        )
        codesy_fee.save()

        total_fees = paypal_fee.amount + codesy_fee.amount
        codesy_payout.amount = codesy_payout.amount - total_fees
        codesy_payout.save()
        # attempt paypay payout
        # paypal id are limited to 30 chars
        # TODO: Fix this potential non-unique key
        paypay_key = str(codesy_payout.transaction_key)[:30]
        paypal_payout = PaypalPayout({
            "sender_batch_header": {
                "sender_batch_id": paypay_key,
                "email_subject": "Your codesy payout is here!"
            },
            "items": [
                {
                    "recipient_type": "EMAIL",
                    "amount": {
                        "value": int(codesy_payout.amount),
                        "currency": "USD"
                    },
                    "receiver": "DevGirl@mozilla.org",
                    "note": "You have a fake payment waiting.",
                    "sender_item_id": paypay_key
                }
            ]
        })
        # record confirmation in payout
        if paypal_payout.create(sync_mode=True):
            for item in paypal_payout.items:
                if item.transaction_status == "SUCCESS":
                    codesy_payout.api_success = True
                    codesy_payout.confirmation = item.payout_item_id
                codesy_payout.save()
                self.status = "Paid"
                self.save()
            return True
        else:
            return False


@receiver(post_save, sender=Claim)
def notify_matching_offerers(sender, instance, created, **kwargs):
    # Only notify when the claim is first created
    if not created:
        return True

    # TODO: make a nicer HTML email template
    OFFERER_NOTIFICATION_EMAIL_STRING = """
    {user} has claimed the payout for {url}.

    codesy.io will pay your offer of {offer} to {user}.

    To approve or reject this claim, go to:
    https://{site}{claim_link}
    """
    current_site = Site.objects.get_current()

    self_Q = models.Q(user=instance.user)
    offered0_Q = models.Q(offer=0)
    others_bids = Bid.objects.filter(
        issue=instance.issue
    ).exclude(
        self_Q | offered0_Q
    )

    for bid in others_bids:
        send_mail(
            "[codesy] %(user)s has claimed payout for %(url)s" %
            (
                {'user': instance.user, 'url': instance.issue.url}
            ),
            OFFERER_NOTIFICATION_EMAIL_STRING.format(
                user=instance.user,
                url=instance.issue.url,
                offer=bid.offer,
                site=current_site,
                claim_link=instance.get_absolute_url()
            ),
            settings.DEFAULT_FROM_EMAIL,
            [bid.user.email]
        )


@receiver(post_save, sender=Bid)
@receiver(post_save, sender=Issue)
@receiver(post_save, sender=Claim)
def save_title(sender, instance, **kwargs):
    if isinstance(instance, Claim):
        url = instance.evidence
    else:
        url = instance.url

    try:
        r = requests.get(url)
        title_search = re.search('(?:<title.*>)(.*)(?:<\/title>)', r.text)
        if title_search:
            title = HTMLParser.HTMLParser().unescape(title_search.group(1))
            type(instance).objects.filter(id=instance.id).update(title=title)
    except:
        pass


class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    claim = models.ForeignKey(Claim)
    # TODO: Vote.approved needs null=True or blank=False
    approved = models.BooleanField(default=None, blank=True)
    created = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        unique_together = (("user", "claim"),)

    def __unicode__(self):
        return u'Vote for %s by (%s): %s' % (
            self.claim, self.user, self.approved
        )


@receiver(post_save, sender=Vote)
def update_claim_status(sender, instance, created, **kwargs):
    claim = instance.claim
    offers_needed = claim.offers.count()

    if claim.num_votes > 0:
        claim.status = "Pending"
        claim.save()

    if claim.num_approvals == offers_needed:
        claim.status = "Approved"
        claim.save()

    if offers_needed > 0:
        if (claim.num_rejections / float(offers_needed)) >= 0.5:
            claim.status = "Rejected"
            claim.save()


@receiver(post_save, sender=Vote)
def notify_approved_claim(sender, instance, created, **kwargs):
    claim = instance.claim
    votes_needed = claim.offers.count()

    if claim.num_rejections == votes_needed:
        current_site = Site.objects.get_current()
        # TODO: make a nicer HTML email template
        CLAIM_REJECTED_EMAIL_STRING = """
        Your claim for {url} has been rejected.
        https://{site}
        """
        send_mail(
            "[codesy] Your claimed has been rejected",
            CLAIM_REJECTED_EMAIL_STRING.format(
                url=claim.issue.url,
                site=current_site,
            ),
            settings.DEFAULT_FROM_EMAIL,
            [claim.user.email]
        )

    if votes_needed == claim.num_approvals:
        current_site = Site.objects.get_current()
        # TODO: make a nicer HTML email template
        CLAIM_APPROVED_EMAIL_STRING = """
        Your claim for {url} has been approved.
        https://{site}
        """
        send_mail(
            "[codesy] Your claimed has been approved",
            CLAIM_APPROVED_EMAIL_STRING.format(
                url=claim.issue.url,
                site=current_site,
            ),
            settings.DEFAULT_FROM_EMAIL,
            [claim.user.email]
        )


class Payment(models.Model):
    PROVIDER_CHOICES = (
        ('Stripe', 'Stripe'),
        ('PayPal', 'PayPal'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    amount = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, default=0)
    transaction_key = models.CharField(
        max_length=255, default=uuid.uuid4, blank=True)
    api_success = models.BooleanField(default=False)
    charge_amount = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, default=0)
    confirmation = models.CharField(max_length=255, blank=True)
    created = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        abstract = True


class Offer(Payment):
    bid = models.ForeignKey(Bid, related_name='payments')
    provider = models.CharField(
        max_length=255,
        choices=Payment.PROVIDER_CHOICES,
        default='Stripe')

    def fees(self):
        return OfferFee.objects.filter(offer=self)

    def __unicode__(self):
        return u'Offer payment for bid (%s) paid' % (
            self.bid.id
        )


class Payout(Payment):
    claim = models.ForeignKey(Claim, related_name='payouts')
    provider = models.CharField(
        max_length=255,
        choices=Payment.PROVIDER_CHOICES,
        default='PayPal')

    def __unicode__(self):
        return u'Payout to %s for claim (%s)' % (
            self.user, self.claim.id
        )

    def fees(self):
        return PayoutFee.objects.filter(payout=self)


class Fee(models.Model):
    FEE_TYPES = (
        ('PayPal', 'PayPal'),
        ('Stripe', 'Stripe'),
        ('codesy', 'codesy'),
    )
    fee_type = models.CharField(
        max_length=255,
        choices=FEE_TYPES,
        default='')
    amount = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, default=0)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        abstract = True


class OfferFee(Fee):
    offer = models.ForeignKey(Offer, related_name="offer_fees", null=True)


class PayoutFee(Fee):
    payout = models.ForeignKey(Payout, related_name="payout_fees", null=True)


@receiver(post_save, sender=Payout)
@receiver(post_save, sender=Offer)
@receiver(post_save, sender=Bid)
@receiver(post_save, sender=Claim)
@receiver(post_save, sender=Vote)
def update_datetimes_for_model_save(sender, instance, created, **kwargs):
    if created:
        sender.objects.filter(id=instance.id).update(created=datetime.now())
    else:
        sender.objects.filter(id=instance.id).update(modified=datetime.now())
