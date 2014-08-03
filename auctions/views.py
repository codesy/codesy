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
    API endpoint for bids. Users can only list, create, retrieve, update, or delete their own bids.

    Requests for /bids/?url= with Accept: text/html will receive the HTML form for updating or deleting the user's bid.

    url -- url of an OSS issue or bug
    """
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

    def list(self, request, *args, **kwargs):
        resp = super(BidViewSet, self).list(request, *args, **kwargs)
        if self.request.QUERY_PARAMS.get('url', False):
            self.renderer_classes = (TemplateHTMLRenderer,)
            resp.template_name = "bid.html"
        return resp
