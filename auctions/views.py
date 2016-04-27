# from django.shortcuts import redirect
# from django.core.urlresolvers import reverse
# from django.contrib import messages

from auctions.models import Bid, Claim, Vote
# from codesy.base.models import User

from django.views.generic import TemplateView
# from django.template.response import TemplateResponse
from django.contrib.auth.mixins import LoginRequiredMixin


class BidStatusView(LoginRequiredMixin, TemplateView):
    """
    Requests for /bid/?url= will receive the HTML form for creating a bid (if
    none exists) or updating the user's existing bid.

    url -- url of an OSS issue or bug
    """
    template_name = "addon/widget.html"

    def get_context_data(self, **kwargs):
        url = self.request.GET['url']
        bid = None
        claim = None
        try:
            bid = Bid.objects.get(user=self.request.user, url=url)
            claim = Claim.objects.get(issue=bid.issue)
        except:
            pass
        return dict({'bid': bid, 'claim': claim, 'url': url})


class ClaimStatusView(LoginRequiredMixin, TemplateView):
    """
    Requests for /claim-status/{id} will receive the claim details, along with
    an HTML form for offering bidders to approve or deny the claim.

    id -- id of claim
    """

    template_name = 'claim_status_anyone.html'

    def get_context_data(self, **kwargs):
        claim = None
        vote = None
        try:
            claim = Claim.objects.get(pk=self.kwargs['pk'])
            vote = Vote.objects.get(claim=claim, user=self.request.user)
        except:
            pass

        context = dict({'claim': claim, 'vote': vote})
        if self.request.user == claim.user:
            self.template_name = 'claim_status_claimaint.html'

        return context

#
#
# class VoteViewSet(AutoOwnObjectsModelViewSet):
#     """
#     API endpoint for votes. Users can only access their own votes.
#     """
#     queryset = Vote.objects.all()
#     serializer_class = VoteSerializer
#
#
# # List Views
#
# class BidList(APIView):
#     """List of bids for the User
#     """
#     renderer_classes = (TemplateHTMLRenderer,)
#
#     def get(self, request, format=None):
#         try:
#             bids = Bid.objects.filter(user=self.request.user)
#         except:
#             bids = []
#
#         return Response({'bids': bids}, template_name='bid_list.html')
#
#
# class ClaimList(APIView):
#     """List of claims for the User
#     """
#     renderer_classes = (TemplateHTMLRenderer,)
#
#     def get(self, request, format=None):
#         try:
#             claims = Claim.objects.filter(user=self.request.user)
#             voted_claims = Claim.objects.voted_on_by_user(self.request.user)
#         except:
#             claims = []
#             voted_claims = []
#
#         return Response({'claims': claims, 'voted_claims': voted_claims},
#                         template_name='claim_list.html')
#
#
# class VoteList(APIView):
#     """List of vote by a User
#     """
#     renderer_classes = (TemplateHTMLRenderer,)
#
#     def get(self, request, format=None):
#         try:
#             votes = Vote.objects.filter(user=self.request.user)
#         except:
#             votes = []
#
#         return Response({'votes': votes}, template_name='vote_list.html')
#
#
# class PayoutViewSet(APIView):
#     """Users requesting payout
#     """
#     renderer_classes = (TemplateHTMLRenderer,)
#
#     def post(self, request, format=None):
#
#         try:
#             claim = Claim.objects.get(id=request.POST['claim'])
#             if request.user == claim.user:
#                 if claim.payout_request():
        # messages.success(request._request, 'Your payout was sent')
#         except:
#             messages.error(request._request, "Sorry please try later")
#
#         return redirect(reverse('claim-status',
#                                 kwargs={'pk': claim.id}))
