from django.conf.urls import patterns, url, include

from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'bids', views.BidViewSet)
router.register(r'claims', views.ClaimViewSet)

bid_by_url_patterns = patterns(
    '',
    url(r'^bid/', views.GetBid.as_view()),
)

urlpatterns = patterns(
    '',
    url(r'^', include(bid_by_url_patterns, namespace="bid-by-url")),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework'))
)
