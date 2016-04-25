from django.shortcuts import get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages

from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
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


class BidAPIView(APIView):
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
                claim = Claim.objects.get(issue=bid.issue)
            except Claim.DoesNotExist:
                pass

        resp = Response({'bid': bid,
                         'claim': claim,
                         'url': url},
                        template_name='bid.html')
        return resp


class ClaimViewSet(AutoOwnObjectsModelViewSet):
    """
    API endpoint for claims. Users can only access their own claims.
    """
    queryset = Claim.objects.all()
    serializer_class = ClaimSerializer


class ClaimAPIView(APIView):
    """
    Custom API endpoint for user-centric Claim status page

    Requests for /claim-status/{id} will receive the claim details, along with
    an HTML form for offering bidders to approve or deny the claim.

    id -- id of claim
    """
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request, pk, format=None):
        claim = None
        claim = get_object_or_404(Claim, pk=pk)
        # TODO: keep user without offers from seeing a vote form
        try:
            vote = Vote.objects.get(claim=claim, user=self.request.user)
        except:
            vote = None

        if request.user == claim.user:
            return Response({'claim': claim, 'vote': vote},
                            template_name='claim_status_claimaint.html')
        else:
            return Response({'claim': claim, 'vote': vote},
                            template_name='claim_status_anyone.html')


class VoteViewSet(AutoOwnObjectsModelViewSet):
    """
    API endpoint for votes. Users can only access their own votes.
    """
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer


# List Views

class BidList(APIView):
    """List of bids for the User
    """
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request, format=None):
        try:
            bids = Bid.objects.filter(user=self.request.user)
        except:
            bids = []

        return Response({'bids': bids}, template_name='bid_list.html')


class ClaimList(APIView):
    """List of claims for the User
    """
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request, format=None):
        try:
            claims = Claim.objects.filter(user=self.request.user)
            voted_claims = Claim.objects.voted_on_by_user(self.request.user)
        except:
            claims = []
            voted_claims = []

        return Response({'claims': claims, 'voted_claims': voted_claims},
                        template_name='claim_list.html')


class VoteList(APIView):
    """List of vote by a User
    """
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request, format=None):
        try:
            votes = Vote.objects.filter(user=self.request.user)
        except:
            votes = []

        return Response({'votes': votes}, template_name='vote_list.html')


class PayoutViewSet(APIView):
    """Users requesting payout
    """
    renderer_classes = (TemplateHTMLRenderer,)

    def post(self, request, format=None):

        try:
            claim = Claim.objects.get(id=request.POST['claim'])
            if request.user == claim.user:
                if claim.payout_request():
                    messages.success(request._request, 'Your payout was sent')
        except:
            messages.error(request._request, "Sorry please try later")

        return redirect(reverse('custom-urls:claim-status',
                                kwargs={'pk': claim.id}))
