from django.test import TestCase

import payments.utils as payments

class PaymentAmountTest(TestCase):

    def test_calculate_amounts(self):
        amounts = [10,2,3,5,7,9,200,333,999]
        for amount in amounts:

            offer_values = payments.offer_amounts(amount)

            for comp in offer_values:
                print u'%s : %s' % (comp, offer_values[comp])

            total_components = (
                amount + 1 +
                offer_values['codesy_fee'] +
                offer_values['stripe_fee']
            )

            self.assertEqual(
                total_components,
                offer_values['charge_amount']
            )
