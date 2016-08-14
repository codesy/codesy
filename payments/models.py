import json
from decimal import Decimal

from django.conf import settings
from django.db import models

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def get_customer_token(user):
    new_customer = stripe.Customer.create(
        source=user.stripe_card,
        email=user.email
    )
    if new_customer:
        return new_customer.id


class StripeAccount(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    account_id = models.CharField(max_length=100, blank=True)
    secret_key = models.CharField(max_length=100, blank=True)
    public_key = models.CharField(max_length=100, blank=True)
    available_balance = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, default=0)
    verification = models.TextField(default='', blank=True)

    def identity_verified(self):
        verification = json.loads(self.verification)
        return not verification.due_by

    def new_managed_account(self, bank_account):
        stripe_account = stripe.Account.create(
            country="US",
            managed=True,
            tos_acceptance={
                'date': self.user.tos_acceptance_date,
                'ip': self.user.tos_acceptance_ip,
            },
            external_account=bank_account
        )
        if stripe_account:
            self.account_id = stripe_account.id
            self.secret_key = stripe_account['keys'].secret
            self.public_key = stripe_account['keys'].publishable
            self.save()

    def external_account(self, bank_account):
        if not self.account_id:
            self.new_managed_account(bank_account)
        else:
            stripe_account = stripe.Account.retrieve(self.account_id)
            stripe_account.external_account = bank_account
            stripe_account.save()


class StripeEvent(models.Model):
    event_id = models.CharField(primary_key=True, max_length=100, blank=True)
    type = models.CharField(max_length=100, blank=True)
    message_text = models.TextField()
    processed = models.BooleanField(default=False)

    def message(self):
        return json.loads(self.message_text)

    def save(self, *args, **kwargs):
        try:
            webhooks[self.type].process(self)
        except KeyError:
            pass
        super(StripeEvent, self).save(*args, **kwargs)

webhooks = {}


class AccountUpdatedProcessor(object):
    def process(self, event):
        message = event.message()
        account_id = message['user_id']
        try:
            account = StripeAccount.objects.get(account_id=account_id)
            verification = (
                message['data']['object']['verification']
            )
            account.verification = json.dumps(verification)
            account.save()
        except StripeAccount.DoesNotExist:
            # TODO: Tell someone this happened
            pass

webhooks['account.updated'] = AccountUpdatedProcessor()


class BalanceAvailableProcessor(object):
    def process(self, event):
        message = event.message()
        account_id = message['user_id']
        try:
            account = StripeAccount.objects.get(account_id=account_id)
            amount = Decimal(
                message['data']['object']['available'][0]['amount'])
            account.available_balance = (amount / 100)
            account.save()
        except StripeAccount.DoesNotExist:
            pass

webhooks['balance.available'] = BalanceAvailableProcessor()


class ChargeUpdatedProcessor(object):
    def process(self, event):
        message = event.message()
        account_id = message['user_id']
        try:
            pass
        except:
            pass

webhooks['charge.updated'] = ChargeUpdatedProcessor()
