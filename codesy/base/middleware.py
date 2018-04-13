from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect


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


class AlwaysWWW(object):
    """
    Always redirect users to www.codesy.io so they don't get HSTS pinned to
    https://codesy.io which breaks GitHub auth
    """
    def process_request(self, request):
        if (
            settings.DEBUG or
            request.get_host() == "testserver" or
            request.get_host().startswith("codesy-stage")
        ):
            return
        if not request.get_host().startswith("www"):
            return HttpResponseRedirect(
                request.scheme +
                '://www.' +
                request.get_host() +
                request.get_full_path()
            )
