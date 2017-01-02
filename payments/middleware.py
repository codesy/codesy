from django.contrib import messages


class IdentityVerificationMiddleware(object):
    """
    Middleware that checks user verification.
    """

    def process_request(self, request):
        if request.method == 'GET':
            if hasattr(request.user, 'account'):
                user_account = request.user.account()
                if not user_account.identity_verified():
                    messages.warning(request, 'stripe_info_verify')
