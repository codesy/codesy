from decimal import Decimal

from django.test import TestCase

from .. import utils

#import csv

class PaymentAmountTest(TestCase):

    def test_calculate_amounts(self):
        amounts = range(1, 1000)
        #with open('new_tests.csv', 'wb') as csvfile:
            #fieldnames = 'amount', 'charge_amount', 'payout_amount', 'codesy_fee', 'total_stripe_fee', 'offer_stripe_fee' , 'payout_stripe_fee', 'offer_fee', 'payout_fee', 'application_fee', 'gross_transfer_fee', 'actual_transfer_fee', 'charge_stripe_fee','payout_alt_calc', 'payout_overage', 'miscalculation_of_total_stripe_fee', 'iterations'
            #test_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            #test_writer.writeheader()
        nonconvergances=0
        nonconvergance_rate=0
        amount_count=0
        
        for amount in amounts:
            print "---"
            offer_values = utils.transaction_amounts(amount)
            #test_writer.writerow(offer_values)

            for comp in offer_values:
                print u'%s : %s' % (comp, offer_values[comp])

            #Application fee is made up of 2 codesyfees, the fee from stripe for 
            #the credit card charnge, and the fee from stripe for the transfer
            application_fee_components = (
                2*offer_values['codesy_fee'] + 
                offer_values['charge_stripe_fee'] +
                offer_values['actual_transfer_fee']
            )

            self.assertEqual(
                application_fee_components,
                offer_values['application_fee']
            )

            #Application fee is also made up of the total fees the offer is 
            #covering and the total fees the payout is covering.
            application_fee_components = (
                offer_values['offer_fee'] +
                offer_values['payout_fee']
            )

            self.assertEqual(
                application_fee_components,
                offer_values['application_fee']
            )

            #The amount and offer fees always add up to the charge amount
            self.assertEqual(
                amount + offer_values['offer_fee'],
                offer_values['charge_amount']
            )

            #The payout amount and fees add up to the amount, unless the 
            #application fee has an odd penny.
            payout_test = abs(offer_values['payout_amount'] + offer_values['payout_fee'] - amount) <= 0.01

            self.assertEqual(
                True,
                payout_test
            )

            #The payout amount and application fee should add up to the charge amount
            #unless the solution does not coverge.
            application_fee_test = abs(offer_values['payout_amount'] + offer_values['application_fee'] - offer_values['charge_amount']) <= 0.01

            self.assertEqual(
                True,
                application_fee_test
            )

            #The non-covergance rate should be low
            amount_count += 1.0

            payout_test = (offer_values['payout_amount'] + offer_values['payout_fee'] == amount)

            application_fee_test = (offer_values['payout_amount'] + offer_values['application_fee'] == offer_values['charge_amount'])

            if not(payout_test and application_fee_test):
                nonconvergances += 1.0

            nonconvergance_rate = float(nonconvergances/amount_count)
            print u'n nonconvergances = %s, amount_count = %s, nonconvergance_rate = %s' % (nonconvergances, amount_count, nonconvergance_rate)

            self.assertEqual(
                True,
                nonconvergance_rate < (2.0/500)
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
            self.assertEqual(values['total_stripe_fee'], Decimal('2.06'))
            self.assertEqual(values['application_fee'], Decimal('4.56'))
            self.assertEqual(values['codesy_fee'], Decimal('1.25'))
            self.assertEqual(values['charge_amount'], Decimal('52.28'))
            self.assertEqual(values['offer_stripe_fee'], Decimal('1.03'))
            self.assertEqual(values['payout_amount'], Decimal('47.72'))
            self.assertEqual(values['payout_stripe_fee'], Decimal('1.03'))
            self.assertEqual(values['actual_transfer_fee'], Decimal('0.24'))
