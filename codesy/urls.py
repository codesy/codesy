from django.conf.urls import patterns, include, url
from django.contrib import admin

from . import views

admin.site.site_header = u'Codesy administration'
admin.site.site_title = u'Codesy site admin'

# separating stripe, probably a django app in the future
stripe_urls = patterns(
    '',
    url(r'^events', views.StripeHookView.as_view(), name='events'),
    url(r'^terms', views.AcceptTermsView.as_view(), name='terms'),
    url(r'^identity', views.VerifyIdentityView.as_view(), name='identity'),
    url(r'^bank$', views.BankAccountView.as_view(), name='bank'),
    url(r'^card$', views.CreditCardView.as_view(), name='card'),

)

urlpatterns = patterns(
    '',
    # Static home/ explanation pages
    url(r'^$', views.Home.as_view(), name='home'),
    url(r'^legal-info$', views.LegalInfo.as_view(), name='legal-info'),
    # allauth
    (
        r'^accounts/logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/'}
    ),
    url(r'^accounts/', include('allauth.urls')),

    # admin site
    url(r'^admin/', include(admin.site.urls)),

    # auction and widget
    url(r'^', include('auctions.urls')),

    # stripe
    url(r'^stripe/', include(stripe_urls)),

    # API docs
    url(r'^api/docs/', include('rest_framework_swagger.urls')),

    # auctions API
    url(r'^', include('api.urls')),
)
