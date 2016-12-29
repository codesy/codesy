from django.contrib import messages


def IdentityVerificationMiddleware(get_response):
    def middleware(request):
        import ipdb; ipdb.set_trace()
        user_account = request.user.account()
        if user_account.identity_verified():
            messages.warning('stripe_info_verify')
        response = get_response(request)
        return response

    return middleware
