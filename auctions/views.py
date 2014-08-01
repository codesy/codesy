from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework import viewsets

from .models import Bid, Profile
from .serializers import BidSerializer, ProfileSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for profiles.
    """
    model = Profile
    serializer_class = ProfileSerializer

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)


class BidViewSet(viewsets.ModelViewSet):
    """
    API endpoint for bids. Users can create, update, retrieve, and delete only
    their own bids.
    """
    model = Bid
    serializer_class = BidSerializer
    renderer_classes = (TemplateHTMLRenderer,)
    template_name = "bid.html"
    lookup_field = 'url'
    lookup_url_kwarg = 'url'

    def pre_save(self, obj):
        obj.user = self.request.user

    def get_queryset(self):
        return Bid.objects.filter(user=self.request.user)
