from django.forms import ValidationError

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


REMOVE_MESSAGE = 'You must keep at least one connected account.'


class CodesyAccountAdapter(DefaultAccountAdapter):

    def is_open_for_signup(self, request):
        """
        Disable regular signup to require social signup.
        See https://github.com/pennersr/django-allauth/issues/345
        """
        return False


class CodesySocialAccountAdapter(DefaultSocialAccountAdapter):

    def is_open_for_signup(self, request, sociallogin):
        """
        Enable social signup.
        """
        return True

    def validate_disconnect(self, account, accounts):
        """
        Don't let users disconnect their last social account.
        """
        if len(accounts) == 1:
            raise ValidationError(REMOVE_MESSAGE)
