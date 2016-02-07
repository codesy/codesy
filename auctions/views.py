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
    renderer_classes = TemplateHTMLRenderer

    def pre_save(self, obj):
        obj.claimant = self.request.user

    def get_queryset(self):
        return self.queryset.filter(claimant=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created=datetime.now())

    def retrieve (self,request,*args,**kwargs):
        response = super(ClaimViewSet,self).retrieve(request, *args, **kwargs)
        response.template_name = "claim_detail.html"
        return response


class ConfirmClaim(APIView):
    """
    API endpoint for a form to create a claim for an issue.

    Requests for /claims/confirm?bid= will receive the HTML form for creating a
    claim for the issue associated with the bid.

    bid -- id of bid on the issue being claimed
    """
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request, format=None):
        bid = None
        issue = None
        bid_id = self.request.query_params.get('bid')
        try:
            bid = Bid.objects.get(id=bid_id)
            issue = Issue.objects.get(url=bid.url)
        except Bid.DoesNotExist:
            bid = None

        resp = Response({'bid': bid,
                         'issue': issue},
                        template_name='confirm_claim.html')
        return resp
