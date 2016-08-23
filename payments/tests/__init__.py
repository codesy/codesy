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
