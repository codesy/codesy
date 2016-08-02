import json
from decimal import Decimal

from django.conf import settings
from django.db import models

from six import with_metaclass


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


class StripeEvent(models.Model):
    event_id = models.CharField(primary_key=True, max_length=100, blank=True)
    type = models.CharField(max_length=100, blank=True)
    message_text = models.TextField()
    processed = models.BooleanField(default=False)

    def message(self):
        return json.loads(self.message_text)

    def save(self, *args, **kwargs):
        web_hooks[self.type].process(self)
        super(StripeEvent, self).save(*args, **kwargs)


class WebhookRegistry(object):

    def __init__(self):
        self._registry = {}

    def register(self, webhook):
        self._registry[webhook.name] = webhook

    def keys(self):
        return self._registry.keys()

    def __getitem__(self, name):
        try:
            return self._registry[name]()
        except KeyError:
            return Webhook()

web_hooks = WebhookRegistry()
del WebhookRegistry


class Registerable(type):
    def __new__(cls, clsname, bases, attrs):
        newclass = super(Registerable, cls).__new__(cls, clsname, bases, attrs)
        if getattr(newclass, "name", None) is not None:
            web_hooks.register(newclass)
        return newclass


class Webhook(with_metaclass(Registerable, object)):

    def process(self, event):
        pass


class AccountUpdatedWebhook(Webhook):
    name = "account.updated"

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


class BalanceAvailableWebhook(Webhook):
    name = "balance.available"

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
