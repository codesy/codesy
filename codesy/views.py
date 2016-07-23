from django.views.generic import View, TemplateView
from django.shortcuts import redirect
# from django.core.urlresolvers import reverse
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.conf import settings
import datetime


# stripe related:
from codesy.base.models import StripeAccount, StripeEvent
import stripe
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json

stripe.api_key = settings.STRIPE_SECRET_KEY


def cc_debug_ctx():
    if settings.DEBUG:
        return {
            'cc_number': '4111111111111111',
            'cc_ex_month': '01',
            'cc_ex_year': '2020',
            'cvc': '123',
        }


def acct_debug_ctx():
    if settings.DEBUG:
        return {
            'name': 'Joe Sample',
            'routing_number': '110000000',
            'account_number': '000123456789',
        }


class CSRFExemptMixin(object):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CSRFExemptMixin, self).dispatch(*args, **kwargs)


class LegalInfo(TemplateView):
    template_name = 'legal.html'


class Home(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        ctx = super(Home, self).get_context_data(**kwargs)
        ctx['cc_debug'] = cc_debug_ctx()
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


class OfferInfo(TemplateView):
    template_name = 'stripe/credit_card_form.html'

    def get_context_data(self, **kwargs):
        ctx = super(OfferInfo, self).get_context_data(**kwargs)
        ctx['cc_debug'] = cc_debug_ctx()
        return ctx


class CreateManagedAccount(TemplateView):
    template_name = "stripe/create_account.html"

    def post(self, *args, **kwargs):
        """
        create stripe managed account
        """
        import ipdb; ipdb.set_trace()
        try:
            new_account = stripe.Account.create(
                country="US",
                managed=True
            )
            if new_account:
                new_codesy_acct = StripeAccount(
                    user=self.request.user,
                    account_id=new_account.id,
                    secret_key=new_account['keys'].secret,
                    public_key=new_account['keys'].publishable,
                )
                new_account.tos_acceptance.date = datetime.datetime.now()
                new_account.tos_acceptance.ip = (
                    self.request.META.get('REMOTE_ADDR'))
                new_account.save()
                new_codesy_acct.save()

        except Exception as e:
            self.error_message = e.message

        return redirect('payout-info')


class UserHasManagedAccount(UserPassesTestMixin):
    login_url = '/stripe/accept-terms'
    redirect_field_name = None
    def test_func(self):
        return self.request.user.account()

class SaveAccountInfo(UserHasManagedAccount, TemplateView):
    template_name = 'stripe/bank_account_form.html'

    def get_context_data(self, **kwargs):
        ctx = super(SaveAccountInfo, self).get_context_data(**kwargs)
        ctx['acct_debug'] = acct_debug_ctx()
        return ctx

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
