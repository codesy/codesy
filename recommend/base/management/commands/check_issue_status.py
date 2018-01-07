import logging


from django.core.management.base import BaseCommand

from auctions.models import Issue
from ../utils/gh_gql import Issue as ghIssue

logging.basicConfig()

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):

        issues = Issue.objects.all()

        try:
            for issue in issues:
                gh_issue = ghIssue.get(url=issue.url)
                issue.state = gh_issue['resource']['state']
                issue.save()

        except Exception as e:
            logger.error("check_issue_status, error: %s" % e)
