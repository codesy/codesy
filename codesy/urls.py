from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView

from rest_framework import routers

from . import views

admin.site.site_header = u'Codesy administration'
admin.site.site_title = u'Codesy site admin'

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)

urlpatterns = patterns('',
    # Special view for whats-deployed app
    url(r'^revision.txt$', 'codesy.views.revision', name='revision'),

    # Home page
    url(r'^$', 'codesy.views.home', name='home'),

    # Static explanation pages
    url(r'^how-it-works$',
        TemplateView.as_view(template_name="how_it_works.html"),
        name='how_it_works'),
    url(r'^faq$', TemplateView.as_view(template_name="faq.html"), name='faq'),

    #allauth
    url(r'^accounts/', include('allauth.urls')),

    #admin site
    url(r'^admin/', include(admin.site.urls)),

    # API docs
    url(r'^docs/', include('rest_framework_swagger.urls')),

    # auctions API
    url(r'^', include('auctions.urls')),

    # user API
    url(r'^', include(router.urls))
)
