from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings

import stripe
#stripe.api_key = settings.STRIPE_SECRET_KEY

# codesy fee of 2.5% charged to offer and payout
codesy_pct = Decimal('0.05')
#codesy_pct = Decimal('0.05')

# stripe charge of 2.9% for credit card payments
stripe_pct = Decimal('0.029')

# stripe fee of 30 cents for each credit card payment
stripe_transaction = Decimal('0.30')

# stripe charge of 0.5% for transfering to bank account
stripe_transfer_pct = Decimal('0.005')


def round_penny(amount):
    return amount.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)


def calculate_codesy_fee(amount):
    return round_penny(amount * codesy_pct)


def calculate_charge_stripe_fee(offer_charge):
    return round_penny(
        offer_charge * stripe_pct + stripe_transaction
    )


def calculate_transfer_stripe_fee(payout_amount):
    return round_penny(
        payout_amount * stripe_transfer_pct
    )


def transaction_amounts(amount):
    if amount <= 0:
        raise ValueError('Zeros and negatives are not allowed')
    charge_guess = 0
    payout_guess = 0
    codesy_fee_amount = 0
    #Codesy's total 5% fee.
    charge_stripe_fee = 0
    #Stripe's actual fee on the charged amount--should equal Stripe's info.
    transfer_stripe_fee = 0
    #Stripe's actual fee on the payout amount--should equal Stripe's info.
    application_fee = 0
    #total fees taken out
    #Information given to Stripe
    iteration = 0
    calc_charge = 0
    calc_payout = 0

    for iteration in range(0,11):
        #used a while originally, but sometimes the while gets stuck
        charge_guess = calc_charge
        payout_guess = calc_payout
        codesy_fee_amount = calculate_codesy_fee(amount)
        charge_stripe_fee = calculate_charge_stripe_fee(charge_guess)
        transfer_stripe_fee = calculate_transfer_stripe_fee(payout_guess)
        application_fee = codesy_fee_amount + charge_stripe_fee + transfer_stripe_fee
        calc_charge = round_penny(amount + application_fee / 2)
        calc_payout = round_penny(calc_charge - application_fee)  
        #Note: when total fees are uneven, charge gets the extra penny
        if (charge_guess == calc_charge) and (payout_guess == calc_payout):
        #breaks out when guess and calc are equal
            break


    charge_amount = charge_guess
    #Amount charged to the bidder/offerer's card or account
    #information given to Stripe

    payout_amount = payout_guess
    #Amount that ends up in the asker/fixer's bank account

    offer_fee = round_penny(application_fee/2)
    # Part of the fee-split added on to offer. Calculated for testing purposes. Note: when total fees are uneven, offer gets the extra penny

    payout_fee = application_fee - offer_fee
    #part of the fee-split taken out of payout. Calculated for testing purposes. Note: when total fees are uneven, offer gets the extra penny

    payout_alt_calc = (
        charge_amount - application_fee
    )
    #back calculating payout for testing

    payout_overage = (
        payout_alt_calc
        - payout_amount
    )

    total_stripe_fee = charge_stripe_fee + transfer_stripe_fee

    return {
        'amount': amount,
        'charge_amount': charge_amount,
        'payout_amount': payout_amount,
        'codesy_fee': codesy_fee_amount,
        'total_stripe_fee': total_stripe_fee,
        'charge_stripe_fee': charge_stripe_fee,
        'gross_transfer_fee': calculate_transfer_stripe_fee(payout_alt_calc),
        'actual_transfer_fee': transfer_stripe_fee,
        'offer_fee': offer_fee,
        'payout_fee': payout_fee,
        'application_fee': application_fee,
        'payout_alt_calc': payout_alt_calc,
        'payout_overage': payout_overage,
        'miscalculation_of_total_stripe_fee': total_stripe_fee - charge_stripe_fee - transfer_stripe_fee,
        'iterations': iteration
    }


def refund(offer):
    try:
        refund = stripe.Refund.create(
            charge=offer.charge_id
        )
        if refund:
            offer.refund_id = refund.id
    except Exception as e:
        print e.message
        offer.error_message = e.message
    offer.save()
    return offer.error_message == u''


def authorize(offer):
    try:
        # setting 'capture' to false makes this an Authorization request
        authorize = stripe.Charge.create(
            amount=int(offer.charge_amount * 100),
            currency="usd",
            customer=offer.bid.user.stripe_customer,
            description="Offer for: " + offer.bid.url,
            metadata={'bid_id': offer.bid.id},
            capture=False,
        )
        if authorize:
            offer.charge_id = authorize.id
            offer.api_success = True
        else:
            offer.error_message = "Authorization failed, please try later"
    except Exception as e:
        offer.error_message = e.message
    offer.save()


def charge(offer, payout):
    details = transaction_amounts(payout.amount)

    try:
        charge = stripe.Charge.create(
            customer=offer.user.stripe_customer,
            destination=payout.claim.user.account().account_id,
            amount=int(details['charge_amount'] * 100),
            currency="usd",
            description="Payout for: " + offer.bid.url,
            metadata={'bid_id': offer.bid.id},
            application_fee=int(details['application_fee'] * 100)
        )
        if charge:
            payout.charge_amount = details['payout_amount']
            payout.charge_id = charge.id
            payout.api_success = True
            payout.save()

            offer.api_success = True
            offer.charge_id = charge.id
            offer.save()

            payout.claim.status = 'Paid'
            payout.claim.save()
        else:
            offer.error_message = "Authorization failed, please try later"
    except Exception as e:
        print 'charge error: %s' % e.message
        offer.error_message = e.message
    offer.save()
