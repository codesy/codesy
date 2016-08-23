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


def tearDownPackage(self):
    self.patch_stripe.restore()
