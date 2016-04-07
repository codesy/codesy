from decimal import Decimal

from django.shortcuts import get_object_or_404, redirect
from django.conf import settings

from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from auctions.models import Bid, Claim, Vote, Payout
from codesy.base.models import User
from .serializers import (BidSerializer, ClaimSerializer, UserSerializer,
                          VoteSerializer)

import paypalrestsdk
from paypalrestsdk import Payout as PaypalPayout


# TODO: Find a prettier way to authenticate
paypalrestsdk.configure({"mode": settings.PAYPAL_MODE,
                         "client_id": settings.PAYPAL_CLIENT_ID,
                         "client_secret": settings.PAYPAL_CLIENT_SECRET,
                        #  "ssl_options":{"cert": "./api/g5-cacert.pem"},
                         })


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
        try:
            vote = Vote.objects.filter(claim=claim, user=self.request.user)[0]
        except:
            vote = None

        return Response({'claim': claim, 'vote': vote},
                        template_name='claim_status.html')


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
        except:
            claims = []

        return Response({'claims': claims}, template_name='claim_list.html')


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
        claim = Claim.objects.get(id=request.POST['claim'])

        # leave if claim already paid
        if claim.status == 'Paid':
            return reverse('claim-status', pk=claim.id)

        user = request.user
        bid = Bid.objects.get(url=claim.issue.url, user=user)

        # TODO: create Fee objects for this payout
        paypal_fee = Decimal('0.25')
        codesy_fee = bid.ask * Decimal('0.025')

        codesy_payout = Payout.objects.filter(claim=claim)[0]
        if codesy_payout:
            if codesy_payout.confirmation:
                claim.status = 'Paid'
                claim.save()
                return reverse('claim-status', pk=claim.id)

        else:
            codesy_payout = Payout(
                user=user,
                claim=claim,
                amount=bid.ask - codesy_fee,
            )

        codesy_payout.fee = paypal_fee + codesy_fee
        codesy_payout.save()

        # attempt paypay payout
        paypal_payout = PaypalPayout({
            "sender_batch_header": {
                "sender_batch_id": codesy_payout.id,
                "email_subject": "Your codesy payout is here!"
            },
            "items": [
                {
                    "recipient_type": "EMAIL",
                    "amount": {
                        "value": int(codesy_payout.amount),
                        "currency": "USD"
                    },
                    "receiver": "DevGirl@mozilla.org",
                    "note": "You have a fake payment waiting.",
                    "sender_item_id": codesy_payout.id
                }
            ]
        })
        # record confirmation in payout
        if paypal_payout.create(sync_mode=True):
            for item in paypal_payout.items:
                if item.transaction_status == "SUCCESS":
                    codesy_payout.confirmation = item.payout_item_id
                codesy_payout.save()
                claim.status = "Paid"
                claim.save()
        else:
            pass

        return reverse('claim-status', pk=claim.id)
