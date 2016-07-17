from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from django.conf import settings
import datetime

from codesy.base.models import StripeAccount
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

def cc_debug_ctx():
    if settings.DEBUG:
        return {
            'cc_number': '4111111111111111',
            'cc_ex_month': '01',
            'cc_ex_year': '2020',
            'cvc': '123',
        }


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
    template_name = 'card_info.html'

    def get_context_data(self, **kwargs):
        ctx = super(OfferInfo, self).get_context_data(**kwargs)
        ctx['cc_debug'] = cc_debug_ctx()
        return ctx


class PayoutInfo(TemplateView):
    template_name = 'acct_info.html'

    def post(self, *args, **kwargs):
        """
        create or update stripe managed account
        """
        if self.request.user.account():
            # process update
            pass
        else:
            # create new account
            try:
                new_account = stripe.Account.create(
                    country="US",
                    managed=True
                )
                import ipdb; ipdb.set_trace()
                if new_account:
                    import ipdb; ipdb.set_trace()
                    new_codesy_acct = StripeAccount(
                        user=self.request.user,
                        stripe_id=new_account.id,
                        secret_key=new_account['keys'].secret,
                        public_key=new_account['keys'].publishable,
                        tos_acceptance_date=datetime.datetime.now(),
                        tos_acceptance_ip=self.request.META.get('REMOTE_ADDR')
                    )

                    new_codesy_acct.save()
            except Exception as e:
                import ipdb; ipdb.set_trace()
                self.error_message = e.message

        return redirect('payout-info')

class LegalInfo(TemplateView):
    template_name = 'legal.html'
