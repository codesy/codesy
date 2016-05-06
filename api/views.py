from rest_framework.viewsets import ModelViewSet

from auctions.models import Bid, Claim, Vote
from codesy.base.models import User
from .serializers import (BidSerializer, ClaimSerializer, UserSerializer,
                          VoteSerializer)


class UserViewSet(ModelViewSet):
    """
    API endpoint for users. Users can only list, create, retrieve,
    update, or delete themself.
    """
    model = User
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self, qs=None):
        return self.request.user


class AutoOwnObjectsModelViewSet(ModelViewSet):
    """
    Custom ModelViewSet that automatically:
        1. assigns obj.user to self.request.user
        2. restricts queryset to users' own objects
    """
    def pre_save(self, obj):
        obj.user = self.request.user

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class BidViewSet(AutoOwnObjectsModelViewSet):
    """
    API endpoint for bids. Users can only access their own bids.
    """
    queryset = Bid.objects.all()
    serializer_class = BidSerializer


class ClaimViewSet(AutoOwnObjectsModelViewSet):
    """
    API endpoint for claims. Users can only access their own claims.
    """
    queryset = Claim.objects.all()
    serializer_class = ClaimSerializer


class VoteViewSet(AutoOwnObjectsModelViewSet):
    """
    API endpoint for votes. Users can only access their own votes.
    """
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
