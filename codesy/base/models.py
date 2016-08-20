import requests

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.dispatch import receiver
from allauth.account.signals import user_signed_up

from payments.models import StripeAccount, get_customer_token

EMAIL_URL = 'https://api.github.com/user/emails'


class User(AbstractUser):
    # TODO: remove this as we don't need or want to store it
    stripe_card = models.CharField(max_length=100, blank=True)
    stripe_customer = models.CharField(max_length=100, blank=True)
    stripe_bank_account = models.CharField(max_length=100, blank=True)
    tos_acceptance_date = models.DateTimeField(null=True, blank=True)
    tos_acceptance_ip = models.CharField(max_length=20, blank=True)
    USERNAME_FIELD = 'username'

    def get_gravatar_url(self):
        github_account = self.socialaccount_set.get(provider='github')
        return ("https://avatars3.githubusercontent.com/u/%s?v=3&s=96" %
                github_account.uid)

    def accepted_terms(self):
        return (
            not (not self.tos_acceptance_date)
            and
            not (not self.tos_acceptance_ip)
        )

    def account(self):
        try:
            codesy_account = StripeAccount.objects.get(user=self)
            return codesy_account
        except:
            return StripeAccount(user=self)

    def save(self, *args, **kwargs):
        if User.objects.filter(pk=self.pk).exists():
            existing = User.objects.get(pk=self.pk)

            if existing.stripe_card != self.stripe_card:
                customer = get_customer_token(self)
                self.stripe_card = ""
                self.stripe_customer = customer

            if existing.stripe_bank_account != self.stripe_bank_account:
                if not self.stripe_bank_account == "":
                    managed_account = self.account()
                    managed_account.external_account(self.stripe_bank_account)

        super(User, self).save(*args, **kwargs)


@receiver(user_signed_up)
def add_signup_email_and_start_inactive(sender, request, user, **kwargs):
    user.is_active = False
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
        user.save()
