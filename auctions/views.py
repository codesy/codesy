from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Bid, Claim
from .serializers import BidSerializer, ClaimSerializer


class BidViewSet(ModelViewSet):
    """
    API endpoint for bids. Users can only access their own bids.
    """
    queryset = Bid.objects.all()
    serializer_class = BidSerializer

    def pre_save(self, obj):
        # TODO: authorize the user's credit card via balanced
        obj.user = self.request.user

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class GetBid(APIView):
    """
    API endpoint for a single bid form.

    Requests for /bid/?url= will receive the HTML form for creating a bid (if
    none exists) or updating the user's existing bid.

    url -- url of an OSS issue or bug
    """
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request, format=None):
        url = self.request.QUERY_PARAMS.get('url')
        try:
            bid = Bid.objects.get(user=self.request.user, url=url)
        except Bid.DoesNotExist:
            bid = None
        resp = Response({'bid': bid,
                         'url': url},
                        template_name='bid.html')
        return resp


class ClaimViewSet(ModelViewSet):
    """
    API endpoint for claims. Users can only access their own claims.
    """
    queryset = Claim.objects.all()
    serializer_class = ClaimSerializer

    def pre_save(self, obj):
        obj.claimant = self.request.user

    def get_queryset(self):
        return self.queryset.filter(claimant=self.request.user)
