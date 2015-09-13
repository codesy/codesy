import fudge

from django.test import TestCase

from github import UnknownObjectException

from ..utils import issue_state


class IssueStateTest(TestCase):

    def test_issue_state(self):
        url = 'https://github.com/codesy/codesy/issues/158'

        fake_gh_client = fudge.Fake()
        (fake_gh_client.expects('get_repo').with_args('codesy/codesy')
                       .returns_fake().expects('get_issue').with_args(158)
                       .returns_fake().has_attr(state='open'))

        self.assertEqual('open', issue_state(url, fake_gh_client))

    def test_issue_state_catches_UnknownObjectException(self):
        url = 'https://github.com/codesy/codesy/issues/158'

        fake_gh_client = fudge.Fake()
        (fake_gh_client.expects('get_repo').with_args('codesy/codesy')
                       .raises(UnknownObjectException(404,
                                                      "Cannot find repo.")))

        self.assertEqual(None, issue_state(url, fake_gh_client))
