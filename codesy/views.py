import hashlib

from django.views.generic import TemplateView


class Home(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        ctx = super(Home, self).get_context_data(**kwargs)
        ctx['gravatar_url'] = self.get_gravatar_url()
        browser = 'unknown'
        if (hasattr(self.request, 'META') and
                'HTTP_USER_AGENT' in self.request.META):
            browser = self.get_browser()
        ctx['browser'] = browser
        return ctx

    def get_gravatar_url(self):
        email_hash = ''
        if self.request.user.is_authenticated():
            email_hash = hashlib.md5(self.request.user.email).hexdigest()
        return "//www.gravatar.com/avatar/{}?s=40".format(
            email_hash)

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
