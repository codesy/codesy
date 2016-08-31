import json


from django.test import TestCase
from model_mommy import mommy

from ..models import (StripeAccount, StripeEvent, WebHookProcessor,
                      AccountUpdatedProcessor)
from codesy.base.models import User


from . import (
    application_fee_created, balance_available, account_verified,
    account_not_verified, payment_created, account_updated
)


class StripeAccountTest(TestCase):

    def test_get_customer_token(self):
        """
            When a user saves their credit card info stripe provides
            a credit card token.  This token is used once to get a
            customer token when an attempt to save the cc token is made.
            The cc token should not be saved.
        """
        user = mommy.make(User)
        user.save()
        self.assertFalse(user.stripe_customer)
        user.stripe_card = "howdy"
        user.save()
        self.assertFalse(user.stripe_card)
        self.assertEqual("dammit", user.stripe_customer)

    def test_identity_verified(self):
        account = mommy.make(StripeAccount)

        # new accounts should pass
        self.assertTrue(account.identity_verified())

        # test valid verification
        account.verification = account_verified
        self.assertTrue(account.identity_verified())

        # test invalid verification
        account.verification = account_not_verified
        self.assertFalse(account.identity_verified())

    def test_fields_needed(self):
        account = mommy.make(StripeAccount)
        account.verification = account_not_verified
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


class StripeEventTest(TestCase):

    def test_event_with_userid(self):
        event = mommy.make(
            StripeEvent, message_text=json.loads(payment_created)
        )
        self.assertTrue(event.verified)
        self.assertEqual(event.type, 'payment.created')
        self.assertTrue(event.processed)

    def test_event_without_userid(self):
        event = mommy.make(
            StripeEvent, message_text=json.loads(application_fee_created)
        )
        self.assertTrue(event.verified)
        self.assertEqual(event.type, 'payment.created')
        self.assertTrue(event.processed)

    def test_processed_failed(self):
        pass


class WebhookTest(TestCase):

    def test_process_not_implemented(self):
        class test_hook(WebHookProcessor):
            pass
        event = mommy.make(
            StripeEvent, message_text=json.loads(balance_available)
        )
        with self.assertRaises(NotImplementedError):
            test_hook(event=event).process()

    def test_account_updated(self):
        account = mommy.make(StripeAccount, account_id='acct_00000000000000')
        event = mommy.make(StripeEvent,
                           message_text=json.loads('{"id": "evt_1"}'))
        # replace fake retrieved message
        event.message_text = account_updated
        AccountUpdatedProcessor(event=event).process()
        account = StripeAccount.objects.get(pk=account.id)
        self.assertEqual(account.fields_needed,
                         ['legal_entity.verification.document'])
