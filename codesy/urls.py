from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^revision.txt$', 'codesy.views.revision', name='revision'),
    url(r'^braintree_token$', 'codesy.views.braintree_token', name='braintree_token'),
    url(r'^accounts/(\w+)/deposit', 'codesy.views.deposit', name='deposit'),
    url(r'^$', 'codesy.views.home', name='home'),
    url(r'^how-it-works$',
        TemplateView.as_view(template_name="how_it_works.html"),
        name='how_it_works'),
    url(r'^faq$', TemplateView.as_view(template_name="faq.html"), name='faq'),

    url(r'^accounts/', include('allauth.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^', include('auctions.urls'))
)
