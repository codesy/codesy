from decimal import Decimal

from django.test import TestCase

from .. import utils


class PaymentAmountTest(TestCase):

    def test_calculate_amounts(self):
        amounts = range(1, 1000)
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
#            self.assertEqual(
#                offer_components,
#                offer_values['charge_amount']
#            )

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

    def test_fixed_amounts(self):
            values = utils.transaction_amounts(10)
            self.assertEqual(values['total_stripe_fee'], Decimal('0.66'))
            self.assertEqual(values['application_fee'], Decimal('1.16'))
            self.assertEqual(values['codesy_fee'], Decimal('0.25'))
            self.assertEqual(values['charge_amount'], Decimal('10.58'))
            self.assertEqual(values['offer_stripe_fee'], Decimal('0.33'))
            self.assertEqual(values['payout_amount'], Decimal('9.42'))
            self.assertEqual(values['payout_stripe_fee'], Decimal('0.33'))
            self.assertEqual(values['actual_transfer_fee'], Decimal('0.05'))

            values = utils.transaction_amounts(50)
            self.assertEqual(values['total_stripe_fee'], Decimal('2.08'))
            self.assertEqual(values['application_fee'], Decimal('4.58'))
            self.assertEqual(values['codesy_fee'], Decimal('1.25'))
            self.assertEqual(values['charge_amount'], Decimal('52.29'))
            self.assertEqual(values['offer_stripe_fee'], Decimal('1.04'))
            self.assertEqual(values['payout_amount'], Decimal('47.71'))
            self.assertEqual(values['payout_stripe_fee'], Decimal('1.04'))
            self.assertEqual(values['actual_transfer_fee'], Decimal('0.24'))
