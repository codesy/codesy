from django.conf.urls import patterns, url, include

from rest_framework import routers

from . import views


# TODO: create /api/v1/ url space for default API urls
router = routers.DefaultRouter()
router.register(r'bids', views.BidViewSet)
router.register(r'claims', views.ClaimViewSet)
router.register(r'votes', views.VoteViewSet)

custom_endpoint_url_patterns = patterns(
    '',
    url(r'^bid-for-url/', views.BidAPIView.as_view()),
    url(r'^claim-status/(?P<pk>[^/.]+)',
        views.ClaimAPIView.as_view(), name='claim-status'),
)

urlpatterns = patterns(
    '',
    url(r'^', include(custom_endpoint_url_patterns, namespace="custom-urls")),
    url(r'^', include(router.urls)),
    url(
        r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework')
    )
)
