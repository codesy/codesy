import urllib

from django.views.generic import View, TemplateView
from django.shortcuts import redirect
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse
from django.conf import settings
from django.utils import timezone

# stripe related:
from codesy.base.models import User
from codesy.base.mixins import CSRFExemptMixin
from .models import StripeEvent
import json

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def stripe_debug_values():
    if settings.DEBUG:
        return {
            'identity': {
                'day': '04',
                'month': '07',
                'year': '1976',
                'first_name': 'Joe',
                'last_name': 'Example',
                'street': '36 East Cameron',
                'city': 'Tulsa',
                'zip': '74103',
                'state': 'OK',
                'ssn_last_4': '0000',
                'ssn_full': '000000000',
                'business_name': 'Howdy Dammit LLC',
                'business_tax_id': '000000000'
            },
            'card': {
                'cc_number': '4111111111111111',
                'cc_ex_month': '01',
                'cc_ex_year': '2020',
                'cvc': '123',
            },
            'bank': {
                'name': 'Joe Sample',
                'routing_number': '110000000',
                'account_number': '000123456789',
            }
        }


class UserIdentityVerifiedMixin(UserPassesTestMixin):
    login_url = reverse_lazy('identity')
    redirect_field_name = None

    def test_func(self):
        user_account = self.request.user.account()
        try:
            identity_verified = user_account.identity_verified()
        except stripe.error.StripeError as e:
            if "that account does not exist" in e.message:
                messages.warning(self.request, 'stripe_account_error')
            return None
        return identity_verified


class BankAccountTestsMixin(UserPassesTestMixin):
    login_url = reverse_lazy('terms')
    redirect_field_name = None

    def test_func(self):
        # settting the login_url determines redirect if test returns false
        if self.request.user.accepted_terms():
            self.login_url = self.reverse_lazy_with_param('identity')
        else:
            self.login_url = self.reverse_lazy_with_param('terms')
            return False

        user_account = self.request.user.account()
        try:
            identity_verified = user_account.identity_verified()
        except stripe.error.StripeError as e:
            if "that account does not exist" in e.message:
                messages.warning(self.request, 'stripe_account_error')
            return None
        return identity_verified


class CreditCardView(TemplateView):
    template_name = 'credit_card_page.html'

    def get_context_data(self, **kwargs):
        ctx = super(CreditCardView, self).get_context_data(**kwargs)
        ctx['STRIPE_DEBUG'] = stripe_debug_values()
        return ctx


class CodesyRedirectView(TemplateView):

    def reverse_lazy_with_param(self, template_name):
        request_dict = self.request.GET or self.request.POST
        return_param = urllib.urlencode(request_dict)
        return '%s?%s' % (reverse_lazy(template_name), return_param)

    def get_context_data(self, **kwargs):
        ctx = super(TemplateView, self).get_context_data(**kwargs)
        ctx['return_url'] = self.request.GET.get('return_url', '')
        return ctx

    def post(self, *args, **kwargs):
        return redirect(self.reverse_lazy_with_param('bank'))


class BankAccountView(BankAccountTestsMixin, CodesyRedirectView):
    template_name = 'bank_account_page.html'

    def get_context_data(self, **kwargs):
        ctx = super(BankAccountView, self).get_context_data(**kwargs)
        ctx['STRIPE_DEBUG'] = stripe_debug_values()
        return ctx


class AcceptTermsView(CodesyRedirectView):
    template_name = "accept_terms.html"

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def post(self, *args, **kwargs):
        try:
            user = User.objects.get(id=self.request.user.id)
            user.tos_acceptance_date = timezone.now()
            user.tos_acceptance_ip = self.get_client_ip(self.request)
            user.save()
        except User.DoesNotExist:
            pass
        return super(AcceptTermsView, self).post(**kwargs)


class VerifyIdentityView(CodesyRedirectView):
    template_name = 'verify_identity.html'
    identity_fields = ('first_name', 'last_name', 'ssn_last_4',
                       'personal_id_number', 'type', 'business_name',
                       'business_tax_id')
    address_fields = ('line1', 'city', 'postal_code', 'state', )
    dob_fields = ('day', 'month', 'year',)

    def get_context_data(self, **kwargs):
        ctx = super(VerifyIdentityView, self).get_context_data(**kwargs)
        ctx['STRIPE_DEBUG'] = stripe_debug_values()
        codesy_account = self.request.user.account()
        ctx['fields_needed'] = codesy_account.fields_needed
        return ctx

    def post(self, *args, **kwargs):
        codesy_account = self.request.user.account()
        # TODO: Cannot change if account already verified

        if codesy_account:
            posted = self.request.POST
            stripe_acct = stripe.Account.retrieve(codesy_account.account_id)

            for field in self.identity_fields:
                if field in posted:
                    stripe_acct.legal_entity[field] = posted[field]

            for field in self.address_fields:
                if field in posted:
                    stripe_acct.legal_entity.address[field] = posted[field]

            for field in self.dob_fields:
                if field in posted:
                    stripe_acct.legal_entity.dob[field] = posted[field]

            stripe_acct.save()

        return super(VerifyIdentityView, self).post(**kwargs)


class StripeHookView(CSRFExemptMixin, View):

    def post(self, *args, **kwargs):
        message = json.loads(self.request.body)
        event_id = message['id']

        if not StripeEvent.objects.filter(event_id=event_id).exists():
            new_event = StripeEvent(event_id=event_id, message_text=message)
            new_event.save()

        return HttpResponse()
