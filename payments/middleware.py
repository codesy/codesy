from django.contrib import messages

class IdentityVerificationMiddleware(object):
    """
    Middleware that check user verification.
    """

    def process_request(self, request):
        user_account = request.user.account()
        if not user_account.identity_verified():
            messages.warning(request, 'stripe_info_verify')
