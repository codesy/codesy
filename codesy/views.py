from django.views.generic import TemplateView


class Home(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        ctx = super(Home, self).get_context_data(**kwargs)
        browser = 'unknown'
        if (hasattr(self.request, 'META') and
                'HTTP_USER_AGENT' in self.request.META):
            browser = self.get_browser()
        ctx['browser'] = browser
        return ctx

    def get_browser(self):
        browser = 'unknown'
        agent = self.request.META.get('HTTP_USER_AGENT', '')
        if 'Firefox' in agent:
            browser = 'firefox'
        elif 'OPR' in agent:
            browser = 'opera'
        elif 'Chrome' in agent:
            browser = 'chrome'
        return browser


class CardInfo(TemplateView):
    template_name = 'card_info.html'
