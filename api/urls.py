from django.conf.urls import patterns, url, include

from rest_framework import routers

from . import views


# TODO: create /api/v1/ url space for default API urls
router = routers.DefaultRouter()
router.register(r'bids', views.BidViewSet)
router.register(r'claims', views.ClaimViewSet)
router.register(r'votes', views.VoteViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'payouts', views.UserViewSet)


urlpatterns = patterns(
    '',
    url(r'^', include(router.urls)),
    url(
        r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework')
    )
)
