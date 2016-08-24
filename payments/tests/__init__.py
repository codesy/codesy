import json
import fudge


def setUpPackage(self):
    mock_id = fudge.Fake().has_attr(id='dammit')
    mock_ext_acct = (
        fudge.Fake().has_attr(external_account='').provides('save').is_a_stub()
    )

    mock_customer = (
        fudge.Fake().provides('create').returns(mock_id)
    )
    self.patch_stripe = fudge.patch_object(
        'payments.utils.stripe', 'Customer', mock_customer)

    mock_keys = {"id": "acct_12QkqYGSOD4VcegJ",
                 "keys": {"secret": "sk_live_AxSI9q6ieYWjGIeRbURf6EG0",
                          "publishable": "pk_live_h9xguYGf2GcfytemKs5tHrtg"
                          }}

    mock_account = (
        fudge.Fake().provides('create').returns(mock_keys)
        .provides('retrieve').returns(mock_ext_acct)
    )

    self.patch_stripe = fudge.patch_object(
        'payments.utils.stripe', 'Account', mock_account)

    evt_resp = json.loads(payment_created)

    mock_event = (
        fudge.Fake().provides('retrieve').has_attr(verified=True)
        .returns(evt_resp)
    )

    self.patch_stripe = fudge.patch_object(
        'payments.utils.stripe', 'Event', mock_event)


def tearDownPackage(self):
    self.patch_stripe.restore()


# test constants below:
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

payment_created = """
{
    "id": "evt_18lHxJFizJPFF3oAo6XPXCMA",
    "object": "event",
    "api_version": "2016-03-07",
    "created": 1471870509,
    "data": {
        "object": {
            "id": "py_18lHxIFizJPFF3oAIA4pDgRh",
            "object": "charge",
            "amount": 4696,
            "amount_refunded": 0,
            "application_fee": "fee_93OkjdBJjcAv8W",
            "balance_transaction": "txn_18lHxIFizJPFF3oAcZHnUpYR",
            "captured": true,
            "created": 1471870508,
            "currency": "usd",
            "customer": null,
            "description": null,
            "destination": null,
            "dispute": null,
            "failure_code": null,
            "failure_message": null,
            "fraud_details": {},
            "invoice": null,
            "livemode": false,
            "metadata": {},
            "order": null,
            "paid": true,
            "receipt_email": null,
            "receipt_number": null,
            "refunded": false,
            "refunds": {
                "object": "list",
                "data": [],
                "has_more": false,
                "total_count": 0,
                "url": "/v1/charges/py_18lHxIFizJPFF3oAIA4pDgRh/refunds"
            },
            "shipping": null,
            "source": {
                "id": "acct_16pOYJDanbbP0xsU",
                "object": "account",
                "application_icon": "https://fake.com/stripe-uploads/app.png",
                "application_logo": "https://fake.com/stripe-uploads/app.png",
                "application_name": "codesy",
                "application_url": "https://api.codesy.io/"
            },
            "source_transfer": "tr_18lHxHDanbbP0xsU5aBgTuK6",
            "statement_descriptor": null,
            "status": "succeeded"
        }
    },
    "livemode": false,
    "pending_webhooks": 1,
    "request": "req_93OkgLSR8tn9Sp",
    "type": "payment.created",
    "user_id": "acct_18ec5MFizJPFF3oA"
}
"""

balance_available = """
{
    "created": 1326853478,
    "livemode": false,
    "id": "evt_00000000000000",
    "type": "balance.available",
    "object": "event",
    "request": null,
    "pending_webhooks": 1,
    "api_version": "2016-03-07",
    "data": {
        "object": {
            "object": "balance",
            "available": [
                {
                    "currency": "usd",
                    "amount": 996676,
                    "source_types": {
                        "card": 996676
                    }
                }
            ],
            "livemode": false,
            "pending": [
                {
                    "currency": "usd",
                    "amount": 462,
                    "source_types": {
                        "card": 462
                    }
                }
            ]
        }
    }
}
"""

application_fee_created = """
{
    "created": 1326853478,
    "livemode": false,
    "id": "evt_00000000000000",
    "type": "application_fee.created",
    "object": "event",
    "request": null,
    "pending_webhooks": 1,
    "api_version": "2016-03-07",
    "data": {
        "object": {
            "id": "fee_00000000000000",
            "object": "application_fee",
            "account": "acct_00000000000000",
            "amount": 223,
            "amount_refunded": 0,
            "application": "ca_00000000000000",
            "balance_transaction": "txn_00000000000000",
            "charge": "py_00000000000000",
            "created": 1471941866,
            "currency": "usd",
            "livemode": false,
            "originating_transaction": "ch_18laWDDanbbP0xsU37ZWRWF1",
            "refunded": false,
            "refunds": {
                "object": "list",
                "data": [],
                "has_more": false,
                "total_count": 0,
                "url": "/v1/application_fees/fee_93hwJLJ71zwWXy/refunds"
            }
        }
    }
}
"""

account_updated = """
{
    "created": 1326853478,
    "livemode": false,
    "id": "evt_00000000000000",
    "type": "account.updated",
    "object": "event",
    "request": null,
    "pending_webhooks": 1,
    "api_version": "2016-03-07",
    "data": {
        "object": {
            "id": "acct_00000000000000",
            "object": "account",
            "business_logo": "https://s3.fake.com/icon128.png",
            "business_name": "codesy.io",
            "business_primary_color": "#fefefe",
            "business_url": "https://codesy.io",
            "charges_enabled": true,
            "country": "US",
            "debit_negative_balances": true,
            "decline_charge_on": {
                "avs_failure": false,
                "cvc_failure": true
            },
            "default_currency": "usd",
            "details_submitted": true,
            "display_name": "codesy",
            "email": "test@stripe.com",
            "external_accounts": {
                "object": "list",
                "data": [
                    {
                        "id": "ba_18H1afDanbbP0xsUWUPZzdKu",
                        "object": "bank_account",
                        "account": "acct_16pOYJDanbbP0xsU",
                        "account_holder_name": null,
                        "account_holder_type": null,
                        "bank_name": "BOKF, N.A.",
                        "country": "US",
                        "currency": "usd",
                        "default_for_currency": true,
                        "fingerprint": "uXps2aaol9dObjuq",
                        "last4": "3168",
                        "metadata": {},
                        "routing_number": "103900036",
                        "status": "new"
                    }
                ],
                "has_more": false,
                "total_count": 1,
                "url": "/v1/accounts/acct_16pOYJDanbbP0xsU/external_accounts"
            },
            "legal_entity": {
                "additional_owners": [],
                "address": {
                    "city": "Tulsa",
                    "country": "US",
                    "line1": "36 E Cameron",
                    "line2": null,
                    "postal_code": "74103",
                    "state": "OK"
                },
                "business_name": "codesy.io",
                "business_tax_id_provided": true,
                "dob": {
                    "day": 4,
                    "month": 7,
                    "year": 1962
                },
                "first_name": "John",
                "last_name": "Dungan",
                "personal_id_number_provided": true,
                "ssn_last_4_provided": true,
                "type": "llc",
                "verification": {
                    "details": null,
                    "details_code": null,
                    "document": null,
                    "status": "verified"
                }
            },
            "managed": false,
            "product_description": "codesy.",
            "statement_descriptor": "TEST",
            "support_address": {
                "city": "Tulsa",
                "country": "US",
                "line1": "36 East Cameron",
                "line2": null,
                "postal_code": "74103",
                "state": "OK"
            },
            "support_email": "founders@codesy.io",
            "support_phone": "9187285597",
            "support_url": "",
            "timezone": "America/Chicago",
            "tos_acceptance": {
                "date": 1464657761,
                "iovation_blackbox": "vy4U",
                "ip": "72.213.135.80",
                "user_agent": "Mozilla"
            },
            "transfer_schedule": {
                "delay_days": 2,
                "interval": "manual"
            },
            "transfers_enabled": true,
            "verification": {
                "disabled_reason": null,
                "due_by": 1472261298,
                "fields_needed": [
                    "legal_entity.verification.document"
                ]
            }
        },
        "previous_attributes": {
            "verification": {
                "fields_needed": [],
                "due_by": null
            }
        }
    }
}
"""
