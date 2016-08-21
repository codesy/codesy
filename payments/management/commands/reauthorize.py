from django.core.management.base import BaseCommand
from django.conf import settings
from datetime import timedelta
from django.utils import timezone

import stripe

from auctions.models import Offer
from ... import utils as payments

stripe.api_key = settings.STRIPE_SECRET_KEY


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('day_limit', nargs='+', type=int)

    def handle(self, *args, **options):
        day_limit = options['day_limit'][0]
        expires = timezone.now() - timedelta(days=day_limit)
        offers = Offer.objects.filter(
            refund_id=u'', created__lt=expires
        )

        # TODO:  Add expiration to the oject filter
        for offer in offers:
            payments.refund(offer)
            new_offer = Offer(
                user=offer.user,
                amount=offer.amount,
                bid=offer.bid,
            )
            new_offer.save()

            payments.authorize(new_offer)

            print (
                '%s was refunded. New authorized charge is %s' %
                (offer.charge_id, new_offer.charge_id)
            )
