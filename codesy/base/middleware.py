AUTH_CHANGING_PATHS = ['/accounts/logout/', '/accounts/github/login/callback/']


class AuthChangedMiddleware(object):
    """
    Adds a custom HTTP header for the widget when auth state changes
    """

    def process_response(self, request, response):
        if request.path in AUTH_CHANGING_PATHS:
            response['x-codesy-auth-changed'] = 'true'
        return response
