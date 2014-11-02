from allauth.account.adapter import DefaultAccountAdapter


class CodesyAccountAdapter(DefaultAccountAdapter):

    def is_open_for_signup(self, request):
        """
        Disable regular signup to require GitHub.
        See https://github.com/pennersr/django-allauth/issues/345
        """
        return False
