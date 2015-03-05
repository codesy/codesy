import fudge
from fudge.inspector import arg

from django.conf import settings
from django.db.models.query import QuerySet
from django.test import TestCase
from model_mommy import mommy
import rest_framework

from auctions import models, serializers, views


def _make_test_bid():
    user = mommy.make(settings.AUTH_USER_MODEL)
    url = 'http://gh.com/project'
    bid = mommy.make('auctions.Bid', user=user, url=url)
    return user, url, bid


def _make_test_claim():
    user = mommy.make(settings.AUTH_USER_MODEL)
    url = 'http://gh.com/project'
    issue = mommy.make('auctions.Issue', url=url)
    claim = mommy.make('auctions.Claim', claimant=user, issue=issue)
    return user, url, issue, claim


class BidViewSetTest(TestCase):
    def setUp(self):
        self.viewset = views.BidViewSet()

    def test_attrs(self):
        self.assertIsInstance(
            self.viewset, rest_framework.viewsets.ModelViewSet)
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


class GetBidTest(TestCase):
    def setUp(self):
        self.view = views.GetBid()

    def test_attrs(self):
        self.assertIsInstance(self.view, rest_framework.views.APIView)
        self.assertEqual(
            self.view.renderer_classes,
            (rest_framework.renderers.TemplateHTMLRenderer,)
        )

    @fudge.patch('auctions.views.Response')
    def test_get_existant_bid(self, mock_resp):
        user, url, bid = _make_test_bid()
        self.view.request = fudge.Fake().has_attr(
            user=user, QUERY_PARAMS={'url': url})
        mock_resp.expects_call().with_args(
            {'bid': bid, 'url': url, 'issue': None}, template_name='bid.html')

        self.view.get(self.view.request)

    @fudge.patch('auctions.views.Response')
    def test_get_nonexistant_bid_assigns_None(self, mock_resp):
        user = mommy.make(settings.AUTH_USER_MODEL)
        other_user = mommy.make(settings.AUTH_USER_MODEL)
        url = 'http://gh.com/project'
        mommy.make('auctions.Bid', user=other_user, url=url)
        self.view.request = fudge.Fake().has_attr(
            user=user, QUERY_PARAMS={'url': url})
        mock_resp.expects_call().with_args(
            {'bid': None, 'url': url, 'issue': None}, template_name='bid.html')

        self.view.get(self.view.request)


class ClaimViewSetTest(TestCase):
    def setUp(self):
        self.viewset = views.ClaimViewSet()

    def test_attrs(self):
        self.assertIsInstance(
            self.viewset, rest_framework.viewsets.ModelViewSet)
        self.assertIsInstance(self.viewset.queryset, QuerySet)
        self.assertEqual(self.viewset.queryset.model, models.Claim)
        self.assertEqual(
            self.viewset.serializer_class, serializers.ClaimSerializer)

    def test_pre_save_sets_claimant_to_request_user(self):
        user, url, issue, claim = _make_test_claim()
        self.viewset.request = fudge.Fake().has_attr(user=user)

        self.viewset.pre_save(claim)

        self.assertEqual(claim.claimant, user)

    def test_get_queryset_filters_by_request_user(self):
        user1, url, issue, claim1 = _make_test_claim()
        user2 = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('auctions.Claim', claimant=user2)
        self.viewset.request = fudge.Fake().has_attr(user=user1)

        qs = self.viewset.get_queryset()

        self.assertSequenceEqual(qs.order_by('id'), [claim1, ])

    @fudge.test
    def test_perform_create_saves_created_datetime(self):
        fake_serializer = (
            fudge.Fake('serializers.ClaimSerializer')
            .is_callable()
            .expects('save')
            .with_args(created=arg.any())
        )
        self.viewset.perform_create(fake_serializer)


class ConfirmClaimTest(TestCase):
    def setUp(self):
        self.view = views.ConfirmClaim()

    def test_attrs(self):
        self.assertIsInstance(self.view, rest_framework.views.APIView)
        self.assertEqual(
            self.view.renderer_classes,
            (rest_framework.renderers.TemplateHTMLRenderer,)
        )

    @fudge.patch('auctions.views.Response')
    def test_get_existant_bid_returns_confirm_claim_form(self, mock_resp):
        user, url, bid = _make_test_bid()
        issue = mommy.make('auctions.Issue', url=url)
        self.view.request = fudge.Fake().has_attr(
            QUERY_PARAMS={'bid': bid.id}
        )
        mock_resp.expects_call().with_args(
            {'bid': bid, 'issue': issue},
            template_name='confirm_claim.html'
        )

        self.view.get(self.view.request)

    @fudge.patch('auctions.views.Response')
    def test_get_nonexistant_bid_assigns_None(self, mock_resp):
        self.view.request = fudge.Fake().has_attr(
            QUERY_PARAMS={'bid': 123}
        )
        mock_resp.expects_call().with_args(
            {'bid': None, 'issue': None},
            template_name='confirm_claim.html'
        )

        self.view.get(self.view.request)
