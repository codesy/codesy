from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    '',
    url(r'^addon-login', views.AddonLogin.as_view()),
    url(r'^bid-status/', views.BidStatusView.as_view(), name='bid-status'),
    url(r'^claim-status/(?P<pk>[^/.]+)',
        views.ClaimStatusView.as_view(), name='claim-status'),
    url(r'^bid-list', views.BidList.as_view()),
    url(r'^claim-list', views.ClaimList.as_view()),
    url(r'^vote-list', views.VoteList.as_view()),
)
