from django.conf.urls import patterns, url, include

from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'bids', views.BidViewSet)

single_bid_patterns = patterns('',
    url(r'^bid/', views.GetBid.as_view()),
)

urlpatterns = patterns('',
    url(r'^', include(single_bid_patterns, namespace="single_bid")),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)
