import json


from django.test import TestCase
from model_mommy import mommy

from ..models import StripeAccount
from codesy.base.models import User


account_verified = json.loads(
    """
        {
            "due_by": null,
            "fields_needed": [],
            "disabled_reason": null
        }
    """
)


account_not_verified = json.loads("""
        {
            "due_by": "null",
            "fields_needed": [
                "legal_entity.first_name",
                "legal_entity.last_name"
            ],
            "disabled_reason": null
        }
""")


class StripeAccountTest(TestCase):

    def test_get_customer_token(self):
        user = mommy.make(User)
        user.save()
        self.assertFalse(user.stripe_customer)
        user.stripe_card = "howdy"
        user.save()
        # stripe card is a one-time use token and should not be saved
        self.assertFalse(user.stripe_card)
        self.assertEqual("dammit", user.stripe_customer)

    def test_identity_verified(self):
        account = mommy.make(StripeAccount)

        # new accounts should pass
        self.assertTrue(account.identity_verified())

        # test valid verification
        account.verification = json.dumps(account_verified)
        self.assertTrue(account.identity_verified())

        # test invalid verification
        account.verification = json.dumps(account_not_verified)
        self.assertFalse(account.identity_verified())

    def test_fields_needed(self):
        account = mommy.make(StripeAccount)
        account.verification = json.dumps(account_not_verified)
        self.assertEqual(
            account.fields_needed,
            ['legal_entity.first_name', 'legal_entity.last_name']
        )

    def test_new_managed_account(self):
        account = mommy.make(StripeAccount)
        account.new_managed_account("howdy")
        retreived_account = StripeAccount.objects.get(pk=account.id)
        self.assertEqual(retreived_account.account_id, "acct_12QkqYGSOD4VcegJ")

    def test_external_account(self):
        account = mommy.make(StripeAccount)
        account.external_account("howdy")
        retreived_account = StripeAccount.objects.get(pk=account.id)
        self.assertEqual(retreived_account.account_id, "acct_12QkqYGSOD4VcegJ")
        account.external_account("howdy")
