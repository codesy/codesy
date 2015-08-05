from datetime import datetime

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver

from mailer import send_mail


class Bid(models.Model):
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
    NOTIFICATION_EMAIL_STRING = """
    Bidders have met your asking price for {url}.

    If you fix the issue, you may claim the payout here:
    https://{site}{claim_confirm_link}
    """
    current_site = Site.objects.get_current()

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
                NOTIFICATION_EMAIL_STRING.format(
                    url=bid.url,
                    site=current_site,
                    claim_confirm_link=reverse('custom-urls:claim-by-bid')
                    + '?bid=%s' % bid.id
                ),
                settings.DEFAULT_FROM_EMAIL,
                [bid.user.email]
            )
            # use .update to avoid recursive signal processing
            Bid.objects.filter(id=bid.id).update(ask_match_sent=datetime.now())


class Issue(models.Model):
    url = models.URLField(unique=True, db_index=True)
    state = models.CharField(max_length=255)
    last_fetched = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'Issue for %s (%s)' % (self.url, self.state)


class Claim(models.Model):
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
    # TODO: rename Claim.claimant to Claim.user
    claimant = models.ForeignKey(settings.AUTH_USER_MODEL)
    created = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(null=True, blank=True, auto_now=True)
    evidence = models.URLField(blank=True)
    status = models.CharField(max_length=2,
                              choices=STATUS_CHOICES,
                              default=OPEN)

    class Meta:
        unique_together = (("claimant", "issue"),)

    def __unicode__(self):
        return u'%s claim on Issue %s (%s)' % (
            self.claimant, self.issue.id, self.status
        )
