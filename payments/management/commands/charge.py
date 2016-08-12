from django.core.management.base import BaseCommand
from django.conf import settings

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

from payments import utils


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('amount', nargs='+', type=int)

    def handle(self, *args, **options):
            amount = options['amount'][0]
            details = utils.transaction_amounts(amount)
            charge_amount = details['charge_amount']
            fee = details['application_fee']

            print details

            charge = stripe.Charge.create(
                customer='cus_8xssHec3HDIwUs',
                destination='acct_18fylUFyyzYSCsjR',
                amount=int(charge_amount * 100),
                currency="usd",
                application_fee=int(fee * 100)
            )

            print charge.id
