from django.test import TestCase
import rest_framework

from auctions import models, serializers


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
            self.serializer.Meta.fields, ('id', 'issue', 'claimant',
                                          'evidence', 'status'))
        self.assertSequenceEqual(
            self.serializer.Meta.read_only_fields, ('id',))
