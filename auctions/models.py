from datetime import datetime

from django.conf import settings
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


@receiver(post_save, sender=Bid)
def notify_matching_askers(sender, instance, **kwargs):
    issue_bids = Bid.objects.filter(url=instance.url).aggregate(Sum('offer'))
    met_asks = (Bid.objects.filter(url=instance.url,
                                   ask__lte=issue_bids['offer__sum'],
                                   ask_match_sent=None)
                           .exclude(ask__lte=0))
    for bid in met_asks:
        send_mail("[codesy] Your ask for %(ask)d for %(url)s has been met" % (
            {'ask': bid.ask, 'url': bid.url}),
            "Bidders have met your asking price for %s." % bid.url,
            settings.DEFAULT_FROM_EMAIL,
            [bid.user.email])
        # use .update to avoid recursive signal processing
        Bid.objects.filter(id=bid.id).update(ask_match_sent=datetime.now())


class Issue(models.Model):
    url = models.URLField(unique=True, db_index=True)
    state = models.CharField(max_length=255)
    last_fetched = models.DateTimeField(auto_now=True)
