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
    API endpoint for bids. Users can only list, create, retrieve, update, or delete their own bids.
    """
    # TODO: configure bid.html template for retrieve action
    model = Bid
    serializer_class = BidSerializer

    def pre_save(self, obj):
        # TODO: charge the user's credit card via balanced
        obj.user = self.request.user

    def get_queryset(self):
        bids = Bid.objects.filter(user=self.request.user)
        url = self.request.QUERY_PARAMS.get('url') or False
        bids = bids.filter(url=url) if url else bids
        return bids
