import json

from dateutil import parser

from django.conf import settings
from django.http import HttpResponse
from django.views.generic import TemplateView, View

from auctions.models import Bid
from codesy.base.mixins import CSRFExemptMixin


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


class SetTimezone(CSRFExemptMixin, View):
    def post(self, *args, **kwargs):
        body_unicode = self.request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        client_date = parser.parse(body_data['clientDateString'])
        client_utc_offset = client_date.utcoffset().seconds
        self.request.session['client_utc_offset'] = client_utc_offset
        return HttpResponse(status=201)
