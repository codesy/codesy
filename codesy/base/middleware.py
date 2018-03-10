from django.contrib import messages


class AuthChangedMiddleware(object):
    """
    Adds a custom HTTP header for the widget when auth state changes
    """

    def process_response(self, request, response):
        for message in messages.get_messages(request):
            if (
                response.status_code == 200 and
                (
                    "Successfully signed in" in message.message or
                    "You have signed out" in message.message
                )
            ):
                response['x-codesy-auth-changed'] = 'true'

        return response
