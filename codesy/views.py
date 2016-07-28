from django.views.generic import View, TemplateView
from django.shortcuts import redirect
# from django.core.urlresolvers import reverse
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse
from django.conf import settings
import datetime
# stripe related:
from codesy.base.models import User, StripeEvent
import stripe
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json

stripe.api_key = settings.STRIPE_SECRET_KEY


def stripe_debug_values():
    if settings.DEBUG:
        return {
            'identity': {
                'dob_day': '04',
                'dob_month': '07',
                'dob_year': '1976',
                'first_name': 'Joe',
                'last_name': 'Example',
                'street': '36 East Cameron',
                'city': 'Tulsa',
                'zip': '74103',
                'state': 'OK',
                'ssn_last_4': '0000',
                'ssn_full': '000000000'
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


# stripe related mixins
class CSRFExemptMixin(object):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CSRFExemptMixin, self).dispatch(*args, **kwargs)


class UserIdentityVerifiedMixin(UserPassesTestMixin):
    login_url = '/stripe/verify-id'
    redirect_field_name = None

    def test_func(self):
        user_account = self.request.user.account()
        if not user_account:
            login_url = '/stripe/accept-terms'
            return False
        return user_account.identity_verified()


class UserHasAcceptedTermsMixin(UserPassesTestMixin):
    login_url = '/stripe/accept-terms'
    redirect_field_name = None

    def test_func(self):
        return self.request.user.accepted_terms()


# web site views
class LegalInfo(TemplateView):
    template_name = 'legal.html'


class Home(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        ctx = super(Home, self).get_context_data(**kwargs)
        ctx['cc_debug'] = stripe_debug_values()
        browser = 'unknown'
        if (hasattr(self.request, 'META') and
                'HTTP_USER_AGENT' in self.request.META):
            browser = self.get_browser()
        ctx['browser'] = browser
        return ctx

    def get_browser(self):
        browser = {'name': 'unknown'}
        agent = self.request.META.get('HTTP_USER_AGENT', '')
        if 'Firefox' in agent:
            browser = settings.EXTENSION_SETTINGS['firefox']
        elif 'OPR' in agent:
            browser = settings.EXTENSION_SETTINGS['opera']
        elif 'Chrome' in agent:
            browser = settings.EXTENSION_SETTINGS['chrome']
        return browser


# stripe views
class CreditCardView(TemplateView):
    template_name = 'stripe/credit_card_page.html'

    def get_context_data(self, **kwargs):
        ctx = super(CreditCardView, self).get_context_data(**kwargs)
        ctx['STRIPE_DEBUG'] = stripe_debug_values()
        return ctx


class BankAccountView(UserHasAcceptedTermsMixin, TemplateView):
    template_name = 'stripe/bank_account_page.html'

    def get_context_data(self, **kwargs):
        ctx = super(BankAccountView, self).get_context_data(**kwargs)
        ctx['STRIPE_DEBUG'] = stripe_debug_values()
        return ctx


class AcceptTermsView(TemplateView):
    template_name = "stripe/accept_terms.html"

    def post(self, *args, **kwargs):
        try:
            user = User.objects.get(id=self.request.user.id)
            user.tos_acceptance_date = datetime.datetime.now()
            user.tos_acceptance_ip = self.request.META.get('REMOTE_ADDR')
            user.save()
        except User.DoesNotExist:
            pass
        return redirect('bank-info')


class VerifyIdentityView(TemplateView):
    template_name = 'stripe/verify_identity.html'

    def get_context_data(self, **kwargs):
        ctx = super(VerifyIdentityView, self).get_context_data(**kwargs)
        ctx['STRIPE_DEBUG'] = stripe_debug_values()
        return ctx

    def post(self, *args, **kwargs):
        codesy_account = self.request.user.account()
        if codesy_account:
            posted = self.request.POST
            dob = {
                'day': posted['dob_day'],
                'month': posted['dob_month'],
                'year': posted['dob_year']
            }
            stripe_acct = stripe.Account.retrieve(codesy_account.account_id)
            stripe_acct.legal_entity.dob = dob
            stripe_acct.legal_entity.first_name = posted['first_name']
            stripe_acct.legal_entity.last_name = posted['last_name']
            stripe_acct.legal_entity.address.line1 = posted['address_line1']
            stripe_acct.legal_entity.address.city = posted['address_city']
            stripe_acct.legal_entity.address.postal_code = (
                posted['address_postal_code'])
            stripe_acct.legal_entity.address.state = posted['address_state']
            stripe_acct.legal_entity.ssn_last_4 = posted['ssn_last_4']
            stripe_acct.legal_entity.personal_id_number = (
                posted['personal_id_number'])
            stripe_acct.legal_entity.type = posted['type']
            stripe_acct.save()
            return redirect('account-info')


class StripeHookView(CSRFExemptMixin, View):

    def post(self, *args, **kwargs):
        message = json.loads(self.request.body)
        new_event = StripeEvent(
            event_id=message['id'],
            type=message['type'],
            message_text=json.dumps(message)
        )
        new_event.save()

        return HttpResponse()
