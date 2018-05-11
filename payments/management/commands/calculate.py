import pprint
from decimal import Decimal

from django.core.management.base import BaseCommand

from ... import utils

pp = pprint.PrettyPrinter(indent=4, width=-1)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('amount', nargs='+', type=float)

    def handle(self, *args, **options):
            amount = options['amount'][0]
            amount = Decimal(amount)
            details = utils.transaction_amounts(amount)
            pp.pprint(details)
