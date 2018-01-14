from django.views.generic import TemplateView
from django.conf import settings

from auctions.models import Bid


class LegalInfo(TemplateView):
    template_name = 'legal.html'


class Home(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        ctx = super(Home, self).get_context_data(**kwargs)
        browser = 'unknown'
        if (hasattr(self.request, 'META') and
                'HTTP_USER_AGENT' in self.request.META):
            browser = self.get_browser()
        ctx['browser'] = browser
        ctx['bids'] = Bid.objects.order_by('-modified')[:3]
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
