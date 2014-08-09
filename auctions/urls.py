from django.conf.urls import patterns, url, include

from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'bids', views.BidViewSet)
router.register(r'profiles', views.ProfileViewSet)

urlpatterns = patterns('',
    url(r'^bid/', views.GetBid.as_view()),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)
