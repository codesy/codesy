from django.core.management.base import BaseCommand

from auctions.utils import update_bid_issues, update_issue_states


class Command(BaseCommand):
    def handle(self, *args, **options):
        update_bid_issues()
        update_issue_states()
