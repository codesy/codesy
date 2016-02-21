import fudge

from django.conf import settings
from django.db.models.query import QuerySet
from django.http import Http404
from django.test import TestCase
from model_mommy import mommy
import rest_framework

from codesy.base.models import User
from auctions import models

from .. import serializers, views


class UserViewSetTest(TestCase):
    def setUp(self):
        self.view = views.UserViewSet()

    def test_attrs(self):
        self.assertIsInstance(self.view, views.ModelViewSet)
        self.assertEqual(self.view.model, User)
        self.assertEqual(
            self.view.serializer_class, serializers.UserSerializer)

    def test_get_object(self):
        user = mommy.make(settings.AUTH_USER_MODEL)
        self.view.request = fudge.Fake().has_attr(user=user)

        obj = self.view.get_object()

        self.assertEqual(obj, user)


def _make_test_bid():
    user = mommy.make(settings.AUTH_USER_MODEL)
    url = 'http://gh.com/project'
    issue = mommy.make('auctions.Issue', url=url)
    bid = mommy.make('auctions.Bid', user=user, url=url, issue=issue)
    return user, url, bid


def _make_test_claim():
    user = mommy.make(settings.AUTH_USER_MODEL)
    url = 'http://gh.com/project'
    issue = mommy.make('auctions.Issue', url=url)
    claim = mommy.make('auctions.Claim', user=user, issue=issue)
    return user, url, issue, claim


class BidViewSetTest(TestCase):
    def setUp(self):
        self.viewset = views.BidViewSet()

    def test_attrs(self):
        self.assertIsInstance(
            self.viewset, views.AutoOwnObjectsModelViewSet)
        self.assertIsInstance(self.viewset.queryset, QuerySet)
        self.assertEqual(self.viewset.queryset.model, models.Bid)
        self.assertEqual(
            self.viewset.serializer_class, serializers.BidSerializer)

    def test_pre_save_sets_user_to_request_user(self):
        user, url, bid = _make_test_bid()
        self.viewset.request = fudge.Fake().has_attr(user=user)

        self.viewset.pre_save(bid)

        self.assertEqual(bid.user, user)

    def test_get_queryset_filters_by_request_user(self):
        user1, url, bid1 = _make_test_bid()
        user2 = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('auctions.Bid', user=user2)
        mommy.make('auctions.Bid', user=user2)
        bid4 = mommy.make('auctions.Bid', user=user1)
        bid5 = mommy.make('auctions.Bid', user=user1)
        self.viewset.request = fudge.Fake().has_attr(user=user1)

        qs = self.viewset.get_queryset()

        self.assertSequenceEqual(qs.order_by('id'), [bid1, bid4, bid5])


class BidAPIViewTest(TestCase):
    def setUp(self):
        self.view = views.BidAPIView()

    def test_attrs(self):
        self.assertIsInstance(self.view, rest_framework.views.APIView)
        self.assertEqual(
            self.view.renderer_classes,
            (rest_framework.renderers.TemplateHTMLRenderer,)
        )

    @fudge.patch('api.views.Response')
    def test_get_existant_bid(self, mock_resp):
        user, url, bid = _make_test_bid()
        self.view.request = fudge.Fake().has_attr(
            user=user, query_params={'url': url})
        mock_resp.expects_call().with_args(
            {'bid': bid, 'url': url, 'claim': None}, template_name='bid.html')

        self.view.get(self.view.request)

    @fudge.patch('api.views.Response')
    def test_get_nonexistant_bid_assigns_None(self, mock_resp):
        user = mommy.make(settings.AUTH_USER_MODEL)
        other_user = mommy.make(settings.AUTH_USER_MODEL)
        url = 'http://gh.com/project'
        mommy.make('auctions.Bid', user=other_user, url=url)
        self.view.request = fudge.Fake().has_attr(
            user=user, query_params={'url': url})
        mock_resp.expects_call().with_args(
            {'bid': None, 'url': url, 'claim': None}, template_name='bid.html')

        self.view.get(self.view.request)

    @fudge.patch('api.views.Response')
    def test_get_existant_bid_with_claim(self, mock_resp):
        user, url, bid = _make_test_bid()
        claim = mommy.make('auctions.Claim', issue=bid.issue, user=user)
        self.view.request = fudge.Fake().has_attr(
            user=user, query_params={'url': url})
        mock_resp.expects_call().with_args(
            {'bid': bid, 'url': url, 'claim': claim}, template_name='bid.html')

        self.view.get(self.view.request)


class ClaimViewSetTest(TestCase):
    def setUp(self):
        self.viewset = views.ClaimViewSet()

    def test_attrs(self):
        self.assertIsInstance(
            self.viewset, views.AutoOwnObjectsModelViewSet)
        self.assertIsInstance(self.viewset.queryset, QuerySet)
        self.assertEqual(self.viewset.queryset.model, models.Claim)
        self.assertEqual(
            self.viewset.serializer_class, serializers.ClaimSerializer)

    def test_pre_save_sets_user_to_request_user(self):
        user, url, issue, claim = _make_test_claim()
        self.viewset.request = fudge.Fake().has_attr(user=user)

        self.viewset.pre_save(claim)

        self.assertEqual(claim.user, user)

    def test_get_queryset_filters_by_request_user(self):
        user1, url, issue, claim1 = _make_test_claim()
        user2 = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('auctions.Claim', user=user2)
        self.viewset.request = fudge.Fake().has_attr(user=user1)

        qs = self.viewset.get_queryset()

        self.assertSequenceEqual(qs.order_by('id'), [claim1, ])


class ClaimAPIViewTest(TestCase):
    def setUp(self):
        self.user1, self.url, self.issue, self.claim1 = _make_test_claim()
        self.view = views.ClaimAPIView()
        self.view.request = fudge.Fake().has_attr(user=self.user1)

    def test_attrs(self):
        self.assertIsInstance(self.view, rest_framework.views.APIView)
        self.assertEqual(
            self.view.renderer_classes,
            (rest_framework.renderers.TemplateHTMLRenderer,)
        )

    def test_get_nonexistant_claim_returns_404(self):
        try:
            self.view.get(self.view.request, 999)
            self.fail("Nonexistant claim should have returned 404")
        except Http404:
            pass

    def test_get_existant_claim_no_votes_returns_claim_status(self):
        resp = self.view.get(self.view.request, self.claim1.pk)
        self.assertEqual(self.claim1, resp.data['claim'])
        self.assertEqual([], list(resp.data['offers']))
        self.assertEqual(False, resp.data['voted'])
        self.assertEqual([], list(resp.data['votes']))

    def test_get_existant_claim_with_votes_returns_claim_status(self):
        user2 = mommy.make(settings.AUTH_USER_MODEL, username='User2')
        vote1 = mommy.make('auctions.Vote', claim=self.claim1, user=user2,
                           approved=True)
        self.view.request = fudge.Fake().has_attr(user=user2)
        resp = self.view.get(self.view.request, self.claim1.pk)
        self.assertEqual(self.claim1, resp.data['claim'])
        self.assertEqual([], list(resp.data['offers']))
        self.assertEqual(True, resp.data['voted'])
        self.assertEqual([vote1], list(resp.data['votes']))


class VoteViewSetTest(TestCase):
    def setUp(self):
        self.viewset = views.VoteViewSet()

    def test_attrs(self):
        self.assertIsInstance(
            self.viewset, views.AutoOwnObjectsModelViewSet)
        self.assertIsInstance(self.viewset.queryset, QuerySet)
        self.assertEqual(self.viewset.queryset.model, models.Vote)
        self.assertEqual(
            self.viewset.serializer_class, serializers.VoteSerializer)
