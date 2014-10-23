from django.contrib.auth.models import AbstractUser
from django.db import models
from django.dispatch import receiver

from allauth.socialaccount.signals import social_account_added
from allauth.account.signals import user_signed_up


class User(AbstractUser):
    balanced_card_href = models.CharField(max_length=100, blank=True)
    balanced_bank_account_href = models.CharField(max_length=100, blank=True)

    USERNAME_FIELD = 'username'


@receiver(social_account_added)
def add_email_from_account(sender, request, sociallogin, **kwargs):
    import ipdb; ipdb.set_trace()

@receiver(user_signed_up)
def add_email_from_signup(sender, request, user, **kwargs):
    import ipdb; ipdb.set_trace()
