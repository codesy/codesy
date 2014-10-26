import requests

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.dispatch import receiver

from allauth.account.signals import user_signed_up


EMAIL_URL = 'https://api.github.com/user/emails'


class User(AbstractUser):
    balanced_card_href = models.CharField(max_length=100, blank=True)
    balanced_bank_account_href = models.CharField(max_length=100, blank=True)

    USERNAME_FIELD = 'username'


@receiver(user_signed_up)
def add_email_from_signup(sender, request, user, **kwargs):
    params = {'access_token': kwargs['sociallogin'].token}
    email_data = requests.get(EMAIL_URL, params=params).json()
    for email_address in email_data:
        if (email_address.get('verified', False) and
                email_address.get('primary', False)):
            user.email = email_address['email']
            user.save()
            break
