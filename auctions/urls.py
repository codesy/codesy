from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    '',
    url(r'^bid-status/', views.BidStatusView.as_view(), name='bid-status'),
    url(r'^claim-status/(?P<pk>[^/.]+)',
        views.ClaimStatusView.as_view(), name='claim-status'),

)


# urlpatterns = patterns(
#     '',
#     url(r'^claim-status/(?P<pk>[^/.]+)',
#         views.ClaimAPIView.as_view(), name='claim-status'),
#     url(r'^bid-status/', views.BidStatusView.as_view(),name='bid-status'),
#     url(r'^bid-list', views.BidList.as_view(), name='bid-list'),
#     url(r'^claim-list', views.ClaimList.as_view(), name='claim-list'),
#     url(r'^vote-list', views.VoteList.as_view(), name='vote-list'),
#     url(r'^payout-request',
#         views.PayoutViewSet.as_view(), name='payout-request'),
#
# )
