from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView

from . import views

admin.site.site_header = u'Codesy administration'
admin.site.site_title = u'Codesy site admin'


urlpatterns = patterns(
    '',
    # Static home/ explanation pages
    url(r'^$', views.Home.as_view(), name='home'),

    # allauth
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout',
         {'next_page': '/'}),
    url(r'^accounts/', include('allauth.urls')),

    # admin site
    url(r'^admin/', include(admin.site.urls)),

    # API docs
    url(r'^api/docs/', include('rest_framework_swagger.urls')),

    # auctions API
    url(r'^', include('api.urls')),
)
