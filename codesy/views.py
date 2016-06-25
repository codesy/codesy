from django.views.generic import TemplateView
from django.conf import settings


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


class CardInfo(TemplateView):
    template_name = 'card_info.html'

    def get_context_data(self, **kwargs):
        ctx = super(CardInfo, self).get_context_data(**kwargs)
        ctx['cc_debug'] = cc_debug_ctx()
        return ctx


class LegalInfo(TemplateView):
    template_name = 'legal.html'
