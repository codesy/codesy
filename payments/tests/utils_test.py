from django.test import TestCase
from payments import utils


class PaymentAmountTest(TestCase):

    def test_calculate_amounts(self):
        amounts = [20, 1, 2, 3, 5, 7, 9, 200, 333, 999]
        # amounts = range(1, 1000)
        for amount in amounts:
            print "---"
            offer_values = utils.transaction_amounts(amount)

            for comp in offer_values:
                print u'%s : %s' % (comp, offer_values[comp])

            offer_components = (
                amount
                + offer_values['codesy_fee']
                + offer_values['offer_stripe_fee']
            )
            self.assertEqual(
                offer_components,
                offer_values['charge_amount']
            )

            payout_components = (
                amount
                - offer_values['codesy_fee']
                - offer_values['payout_stripe_fee']
            )

            self.assertEqual(
                payout_components,
                offer_values['payout_amount']
            )

            self.assertEqual(
                offer_values['payout_amount'],
                (offer_values['charge_amount']
                    - offer_values['application_fee']
                 )
            )

    def test_sandbox_charge(TestCase):
        utils.sandbox_charge(10)
