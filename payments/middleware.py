import stripe

from django.contrib import messages


class IdentityVerificationMiddleware(object):
    """
    Middleware that checks user verification.
    """

    def process_request(self, request):
        if request.method == 'GET':
            if hasattr(request.user, 'account'):
                user_account = request.user.account()
                try:
                    identity_verified = user_account.identity_verified()
                except stripe.error.StripeError as e:
                    if "that account does not exist" in e.message:
                        messages.warning(request, 'stripe_account_error')
                    return None
                if not identity_verified:
                    messages.warning(request, 'stripe_info_verify')
