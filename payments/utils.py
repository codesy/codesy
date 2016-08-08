from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

codesy_pct = Decimal('0.025')
stripe_pct = Decimal('0.029')
stripe_transaction = Decimal('0.30')


def round_penny(amount):
    return amount.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)


def calculate_codesy_fee(amount):
    return round_penny(amount * codesy_pct)


def calculate_stripe_fee(amount):
    return round_penny(
        (amount * stripe_pct) + stripe_transaction
    )


def calculate_charge_amount(amount):
    return round_penny(
        (amount + stripe_transaction)
        / (1 - stripe_pct)
    )


def offer_amounts(amount):
    codesy_fee_amount = calculate_codesy_fee(amount)
    charge_amount = calculate_charge_amount(
        amount +
        codesy_fee_amount
    )
    stripe_fee_amount = (
        charge_amount -
        amount -
        codesy_fee_amount
    )

    return {
        'codesy_fee': codesy_fee_amount,
        'stripe_fee': stripe_fee_amount,
        'charge_amount': charge_amount,
    }


def refund(offer):
    try:
        refund = stripe.Refund.create(
            charge=offer.charge_id
        )
        if refund:
            offer.refund_id = refund.id
            offer.save()
    except Exception as e:
        print e.message
        offer.error_message = e.message
        offer.save()


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
    codesy_fee = calculate_codesy_fee(offer.amount)

    try:
        charge = stripe.Charge.create(
            customer=offer.user.stripe_customer,
            destination=payout.user.account().account_id,
            amount=int(offer.charge_amount * 100),
            currency="usd",
            description="Payout for: " + offer.bid.url,
            metadata={'bid_id': offer.bid.id},
            application_fee=int(codesy_fee * 100)
        )
        if charge:
            payout.charge_id = charge.id
            payout.api_success = True
            payout.save()
            payout.claim.status = 'Paid'
            pay.claim.save()
        else:
            offer.error_message = "Authorization failed, please try later"
    except Exception as e:
        offer.error_message = e.message
    offer.save()
