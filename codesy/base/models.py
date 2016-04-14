import requests
import stripe

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from allauth.account.signals import user_signed_up
from rest_framework.authtoken.models import Token


EMAIL_URL = 'https://api.github.com/user/emails'
stripe.api_key = settings.STRIPE_SECRET_KEY


class User(AbstractUser):
    stripe_account_token = models.CharField(max_length=100, blank=True)
    USERNAME_FIELD = 'username'


@receiver(pre_save, sender=settings.AUTH_USER_MODEL)
def replace_cc_token_with_account_token(sender, instance, **kwargs):
    if not instance.stripe_account_token:
        # this is not an update concerning stripe
        return
    else:
        saved_user = User.objects.get(id=instance.id)
        if saved_user.stripe_account_token:
            # TODO:  This prevents new card accounts must change
            instance.stripe_account_token = saved_user.stripe_account_token
        else:
            new_customer = stripe.Customer.create(
                source=instance.stripe_account_token,
                description=instance.email
            )
            instance.stripe_account_token = new_customer.id


@receiver(user_signed_up)
def add_email_from_signup(sender, request, user, **kwargs):
    params = {'access_token': kwargs['sociallogin'].token}
    email_data = requests.get(EMAIL_URL, params=params).json()
    if email_data:
        verified_emails = [e for e in email_data if e['verified']]
        if not verified_emails:
            return None
        sorted_emails = sorted(verified_emails,
                               key=lambda e: (e['primary'], e['verified']),
                               reverse=True)
        user.email = sorted_emails[0]['email']
        user.save(update_fields=['email'])


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_api_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
