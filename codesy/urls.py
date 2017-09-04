from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import LogoutView

from . import views

admin.site.site_header = u'Codesy administration'
admin.site.site_title = u'Codesy site admin'

urlpatterns = [
    # Static home/ explanation pages
    url(r'^$', views.Home.as_view(), name='home'),
    url(r'^legal-info$', views.LegalInfo.as_view(), name='legal-info'),
    # allauth
    url(r'^accounts/logout/$', LogoutView.as_view(), {'next_page': '/'}),
    url(r'^accounts/', include('allauth.urls')),

    # admin site
    url(r'^admin/', include(admin.site.urls)),

    # auction and widget
    url(r'^', include('auctions.urls')),

    # stripe
    url(r'^payments/', include('payments.urls')),

    # API docs
    url(r'^api/docs/', include('rest_framework_swagger.urls')),

    # auctions API
    url(r'^', include('api.urls')),
]
