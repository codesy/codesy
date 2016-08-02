import requests
import stripe

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.dispatch import receiver
from allauth.account.signals import user_signed_up
# from django.contrib.postgres.fields import JSONField

from .stripe_events import StripeAccount

EMAIL_URL = 'https://api.github.com/user/emails'
stripe.api_key = settings.STRIPE_SECRET_KEY


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
        return self.tos_acceptance_date and self.tos_acceptance_ip

    def account(self):
        try:
            codesy_account = StripeAccount.objects.get(user=self)
            return codesy_account
        except:
            return False

    def save(self, *args, **kwargs):
        if User.objects.filter(pk=self.pk).exists():
            existing = User.objects.get(pk=self.pk)

            if existing.stripe_card != self.stripe_card:
                new_customer = stripe.Customer.create(
                    source=self.stripe_card,
                    email=self.email
                )
                if new_customer:
                    self.stripe_card = ""
                    self.stripe_customer = new_customer.id

            if existing.stripe_bank_account != self.stripe_bank_account:
                bank_account = self.stripe_bank_account
                managed_account = self.account()

                if managed_account:
                    stripe_account = stripe.Account.retrieve(
                        managed_account.account_id)
                    stripe_account.external_account = bank_account
                    stripe_account.save()
                else:
                    if bank_account:
                        stripe_account = stripe.Account.create(
                            country="US",
                            managed=True,
                            tos_acceptance={
                                'date': self.tos_acceptance_date,
                                'ip': self.tos_acceptance_ip,
                            },
                            external_account=bank_account
                        )
                        if stripe_account:
                            new_account = StripeAccount(
                                user=self,
                                account_id=stripe_account.id,
                                secret_key=stripe_account['keys'].secret,
                                public_key=stripe_account['keys'].publishable,
                            )
                            new_account.save()

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
