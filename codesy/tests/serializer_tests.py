from django.test import TestCase
import rest_framework

from codesy import base, serializers


class UserSerializerTest(TestCase):
    def setUp(self):
        self.serializer = serializers.UserSerializer()

    def test_attrs(self):
        self.assertIsInstance(
            self.serializer,
            rest_framework.serializers.HyperlinkedModelSerializer)
        self.assertEqual(self.serializer.Meta.model, base.models.User)
        self.assertEqual(
            self.serializer.Meta.fields,
            ('id', 'username', 'stripe_card_token',
             'balanced_bank_account_href'))
        self.assertEqual(
            self.serializer.Meta.read_only_fields, ('id', 'username'))
