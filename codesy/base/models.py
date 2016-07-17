import requests
import stripe

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from allauth.account.signals import user_signed_up


EMAIL_URL = 'https://api.github.com/user/emails'
stripe.api_key = settings.STRIPE_SECRET_KEY


class User(AbstractUser):
    # TODO: remove this as we don't need or want to store it
    stripe_cc_token = models.CharField(max_length=100, blank=True)
    stripe_customer_token = models.CharField(max_length=100, blank=True)
    USERNAME_FIELD = 'username'

    def get_gravatar_url(self):
        github_account = self.socialaccount_set.get(provider='github')
        return ("https://avatars3.githubusercontent.com/u/%s?v=3&s=96" %
                github_account.uid)

    def account(self):
        return StripeAccount.objects.filter(user=self)


@receiver(pre_save, sender=settings.AUTH_USER_MODEL)
def replace_cc_token_with_account_token(sender, instance, **kwargs):
    if instance.stripe_cc_token:
        new_customer = stripe.Customer.create(
            source=instance.stripe_cc_token,
            email=instance.email
        )
        if new_customer:
            instance.stripe_cc_token = ""
            instance.stripe_customer_token = new_customer.id


@receiver(user_signed_up)
def add_email_from_signup_and_start_inactive(sender, request, user, **kwargs):
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


class StripeAccount(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    stripe_id =  models.CharField(max_length=100, blank=True)
    secret_key = models.CharField(max_length=100, blank=True)
    public_key = models.CharField(max_length=100, blank=True)
    tos_acceptance_date = models.DateTimeField(null=True, blank=True)
    tos_acceptance_ip = models.CharField(max_length=20, blank=True)

# other possible fields:
# legal_entity.address.city
# legal_entity.address.line1
# legal_entity.address.postal_code
# legal_entity.address.state
# legal_entity.business_name
# legal_entity.business_tax_id
# legal_entity.dob.day
# legal_entity.dob.month
# legal_entity.dob.year
# legal_entity.first_name
# legal_entity.last_name
# legal_entity.ssn_last_4
# legal_entity.type
