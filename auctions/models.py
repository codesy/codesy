from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver

from mailer import send_mail


class Bid(models.Model):
    # TODO: add created and modified fields to auctions.models.Bid
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    url = models.URLField()
    issue = models.ForeignKey('Issue', null=True)
    ask = models.DecimalField(max_digits=6, decimal_places=2, blank=True,
                              default=0)
    ask_match_sent = models.DateTimeField(null=True, blank=True)
    offer = models.DecimalField(max_digits=6, decimal_places=2, blank=True,
                                default=0)

    class Meta:
        unique_together = (("user", "url"),)

    def __unicode__(self):
        return u'%s bid on %s' % (self.user, self.url)

    def ask_met(self):
        other_bids = Bid.objects.filter(
            url=self.url
        ).exclude(
            user=self.user
        ).aggregate(
            Sum('offer')
        )

        return other_bids['offer__sum'] >= self.ask


@receiver(post_save, sender=Bid)
def notify_matching_askers(sender, instance, **kwargs):
    # TODO: make a nicer HTML email template
    ASKER_NOTIFICATION_EMAIL_STRING = """
    Bidders have met your asking price for {url}.

    If you fix the issue, you may claim the payout by visiting the issue url:
    {url}
    """

    unnotified_asks = Bid.objects.filter(
        url=instance.url,
        ask_match_sent=None
    ).exclude(
        ask__lte=0,
    )

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
    state = models.CharField(max_length=255)
    last_fetched = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'Issue for %s (%s)' % (self.url, self.state)


class Claim(models.Model):
    # TODO: clean up Claim.status choices
    OPEN = 'OP'
    ESCROW = 'ES'
    PAID = 'PA'
    REJECTED = 'RE'
    STATUS_CHOICES = (
        (None, ''),
        (OPEN, 'Open'),
        (ESCROW, 'Escrow'),
        (PAID, 'Paid'),
        (REJECTED, 'Rejected'),
    )
    issue = models.ForeignKey('Issue')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    created = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(null=True, blank=True, auto_now=True)
    evidence = models.URLField(blank=True)
    status = models.CharField(max_length=2,
                              choices=STATUS_CHOICES,
                              default=OPEN)

    class Meta:
        unique_together = (("user", "issue"),)

    def __unicode__(self):
        return u'%s claim on Issue %s (%s)' % (
            self.user, self.issue.id, self.status
        )

    @property
    def expires(self):
        return self.created + timedelta(days=30)

    # TODO: Claim.get_absolute_url should return claim-status/<pk>
    def get_absolute_url(self):
        return reverse('custom-urls:claim-status', kwargs={'pk': self.id})


@receiver(post_save, sender=Claim)
def notify_matching_offerers(sender, instance, created, **kwargs):
    # Only notify when the claim is first created
    if not created:
        return True

    # TODO: make a nicer HTML email template
    OFFERER_NOTIFICATION_EMAIL_STRING = """
    {user} has claimed the payout for {url}.

    codesy.io will pay your offer of {offer} to {user} on {pay_date}.

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
                pay_date=instance.expires,
                site=current_site,
                claim_link=instance.get_absolute_url()
            ),
            settings.DEFAULT_FROM_EMAIL,
            [bid.user.email]
        )


class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    claim = models.ForeignKey(Claim)
    # TODO: Vote.approved needs null=True or blank=False
    approved = models.BooleanField(default=None, blank=True)
    created = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(null=True, blank=True, auto_now=True)

    def __unicode__(self):
        return u'Vote for %s by (%s): %s' % (
            self.claim, self.user, self.approved
        )


@receiver(post_save, sender=Claim)
@receiver(post_save, sender=Vote)
def update_datetimes_for_model_save(sender, instance, created, **kwargs):
    if created:
        instance.created = datetime.now()
    else:
        instance.modified = datetime.now()
