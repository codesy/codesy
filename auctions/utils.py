import re
from datetime import timedelta

from django.utils import timezone

from decouple import config
from github import Github

from .models import Bid, Issue


GITHUB_ISSUE_RE = re.compile('https://github.com/(.*)/issues/(\d+)')


def github_client():
    return Github(client_id=config('GITHUB_CLIENT_ID'),
                  client_secret=config('GITHUB_CLIENT_SECRET'))


def issue_state(url):
    match = GITHUB_ISSUE_RE.match(url)
    if match:
        repo_name, issue_id = match.groups()
        repo = github_client().get_repo(repo_name)
        issue = repo.get_issue(int(issue_id))
        return issue.state


def update(instance, **kwargs):
    using = kwargs.pop('using', '')
    return instance._default_manager.filter(pk=instance.pk).using(
        using).update(**kwargs)


def update_bid_issues():
    for bid in Bid.objects.filter(issue=None):
        try:
            update(bid, issue=Issue.objects.get(url=bid.url))
        except Issue.DoesNotExist:
            state = issue_state(bid.url)
            if state:
                update(bid,
                       issue=Issue.objects.create(url=bid.url, state=state))


def update_issue_states(since=None):
    since = since or timezone.now() - timedelta(days=1)
    for issue in Issue.objects.filter(last_fetched__lt=since):
        state = issue_state(issue.url)
        if state:
            update(issue, last_fetched=datetime.now(), state=state)
