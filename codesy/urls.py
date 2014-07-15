from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^blog/', include('blog.urls')),

    url(r'^revision.txt$', 'codesy.views.revision', name='revision'),
    url(r'^$', 'codesy.views.home', name='home'),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('auctions.urls'))
)
