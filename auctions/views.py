from django.shortcuts import get_object_or_404

from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Bid
from .serializers import BidSerializer


class BidViewSet(ModelViewSet):
    """
    API endpoint for bids. Users can only list, create, retrieve, update, or delete their own bids.
    """
    model = Bid
    serializer_class = BidSerializer

    def pre_save(self, obj):
        # TODO: charge the user's credit card via balanced
        obj.user = self.request.user

    def get_queryset(self):
        return Bid.objects.filter(user=self.request.user)


class GetBid(APIView):
    """
    API endpoint for a single bid form.

    Requests for /bid/?url= will receive the HTML form for creating a bid (if none exists) or updating the user's existing bid.

    url -- url of an OSS issue or bug
    """
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request, format=None):
        bid = get_object_or_404(Bid,
                                user=self.request.user,
                                url=self.request.QUERY_PARAMS.get('url'))
        return Response({'bid': bid}, template_name='bid.html')
