from django.test import TestCase
import rest_framework

from codesy.base.models import User
from auctions import models

from .. import serializers


class UserSerializerTest(TestCase):
    def setUp(self):
        self.serializer = serializers.UserSerializer()

    def test_attrs(self):
        self.assertIsInstance(
            self.serializer,
            rest_framework.serializers.HyperlinkedModelSerializer)
        self.assertEqual(self.serializer.Meta.model, User)
        self.assertEqual(
            self.serializer.Meta.fields,
            ('id', 'username', 'stripe_card_token',
             'balanced_bank_account_href'))
        self.assertEqual(
            self.serializer.Meta.read_only_fields, ('id', 'username'))


class BidSerializerTest(TestCase):
    def setUp(self):
        self.serializer = serializers.BidSerializer()

    def test_attrs(self):
        self.assertIsInstance(
            self.serializer,
            rest_framework.serializers.ModelSerializer)
        self.assertEqual(self.serializer.Meta.model, models.Bid)
        self.assertSequenceEqual(
            self.serializer.Meta.fields, ('id', 'user', 'url', 'ask', 'offer'))
        self.assertSequenceEqual(
            self.serializer.Meta.read_only_fields, ('id',))


class ClaimSerializerTest(TestCase):
    def setUp(self):
        self.serializer = serializers.ClaimSerializer()

    def test_attrs(self):
        self.assertIsInstance(
            self.serializer,
            rest_framework.serializers.ModelSerializer)
        self.assertEqual(self.serializer.Meta.model, models.Claim)
        self.assertSequenceEqual(
            self.serializer.Meta.fields, ('id', 'issue', 'user',
                                          'evidence', 'status'))
        self.assertSequenceEqual(
            self.serializer.Meta.read_only_fields, ('id',))
