import fudge

from django.conf import settings
from django.db.models.query import QuerySet
from django.test import TestCase
from model_mommy import mommy

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
