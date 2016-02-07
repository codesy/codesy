from datetime import datetime

from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Bid, Claim, Issue
from .serializers import BidSerializer, ClaimSerializer


class BidViewSet(ModelViewSet):
    """
    API endpoint for bids. Users can only access their own bids.
    """
    queryset = Bid.objects.all()
    serializer_class = BidSerializer

    def pre_save(self, obj):
        obj.user = self.request.user

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        bid = serializer.save()
        issue, created = Issue.objects.get_or_create(
            url=bid.url,
            defaults={'state': 'open', 'last_fetched': None}
        )
        bid.issue = issue
        bid.save()


class GetBid(APIView):
    """
    API endpoint for a single bid form.

    Requests for /bid/?url= will receive the HTML form for creating a bid (if
    none exists) or updating the user's existing bid.

    url -- url of an OSS issue or bug
    """
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request, format=None):
        url = self.request.query_params.get('url')
        bid = None
        claim = None
        try:
            bid = Bid.objects.get(user=self.request.user, url=url)
        except Bid.DoesNotExist:
            pass
        else:
            try:
                claim = Claim.objects.get(
                    claimant=self.request.user, issue=bid.issue
                )
            except Claim.DoesNotExist:
                pass

        resp = Response({'bid': bid,
                         'claim': claim,
                         'url': url},
                        template_name='bid.html')
        return resp


class ClaimViewSet(ModelViewSet):
    """
    API endpoint for claims. Users can only access their own claims.
    """
    queryset = Claim.objects.all()
    serializer_class = ClaimSerializer
    renderer_classes = (TemplateHTMLRenderer,)

    def pre_save(self, obj):
        obj.claimant = self.request.user

    def get_queryset(self):
        return self.queryset.filter(claimant=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created=datetime.now())


class ClaimAPIView(APIView):
    """
    Custom API endpoint for user-centric Claim status page

    Requests for /claim-status/{id} will receive the claim details, along with
    an HTML form for offering bidders to approve or deny the claim.

    id -- id of claim
    """
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request, pk, format=None):
        try:
            claim = Claim.objects.get(pk=pk)
        except Claim.DoesNotExist:
            claim = None

        return  Response({'claim': claim}, template_name='claim_detail.html')
