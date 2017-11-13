import logging
import json
import sys

from django.core.management.base import BaseCommand
from django.conf import settings
from django.template.loader import get_template
# from django.template import Context

from mailer import send_mail

import stripe

from ...models import StripeAccount

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY

email_template = get_template('../templates/email/need_validation.html')


class Command(BaseCommand):

    def handle(self, *args, **options):
        accounts = StripeAccount.objects.all()
        for account in accounts:
            try:
                stripe_account = stripe.Account.retrieve(account.account_id)
                if account.verification != stripe_account.verification:
                    account.verification = json.dumps(
                        stripe_account.verification)
                    account.save()
                    if stripe_account.verification.fields_needed:
                        email_context = (
                            {'expiration': stripe_account.verification.due_by})
                        message = email_template.render(email_context)
                        send_mail(
                            '[codesy] Account validation needed',
                            message,
                            settings.DEFAULT_FROM_EMAIL,
                            [account.user.email]
                        )
            except:
                e = sys.exc_info()[0]
                logger.error("Error during check_validation: %s" % e)
