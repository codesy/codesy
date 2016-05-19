from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import messages

from auctions.models import Bid, Claim, Vote

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class BidStatusView(LoginRequiredMixin, TemplateView):
    """
    Requests for /bid/?url= will receive the HTML form for creating a bid (if
    none exists) or updating the user's existing bid.

    url -- url of an OSS issue or bug
    """
    template_name = "addon/widget.html"

    def _get_bid_and_claim(self, url):
        bid = None
        claim = None
        try:
            bid = Bid.objects.get(user=self.request.user, url=url)
            claim = Claim.objects.get(issue=bid.issue)
        except:
            pass
        return (bid, claim)

    def get_context_data(self, **kwargs):
        url = self.request.GET['url']
        bid, claim = self._get_bid_and_claim(url)
        return dict({'bid': bid, 'claim': claim, 'url': url})

    def post(self, *args, **kwargs):
        """
        Save changes to bid and get payment for offer
        """
        url = self.request.POST['url']
        new_ask_amount = self.request.POST['ask']
        new_offer_amount = self.request.POST['offer']

        if not(new_ask_amount) and not(new_offer_amount):
            return
        bid, claim = self._get_bid_and_claim(url)

        if not bid:
            bid = Bid(user=self.request.user, url=url)
            bid.save()

        if new_ask_amount:
            bid.ask = new_ask_amount
            bid.save()

        if new_offer_amount > bid.offer:
            new_offer = bid.make_offer(new_offer_amount)
            if new_offer.request():
                messages.success(self.request, "Thanks for the offer!")
                bid.offer = new_offer_amount
                bid.save()
            else:
                messages.error(self.request, new_offer.error_message)

        # return redirect("%s?url=%s" % (reverse('bid-status'), url))


class ClaimStatusView(LoginRequiredMixin, TemplateView):
    """
    Requests for /claim-status/{id} will receive the claim details, along with
    an HTML form for offering bidders to approve or deny the claim.

    id -- id of claim
    """

    template_name = 'claim_status.html'

    def get_context_data(self, **kwargs):
        claim = None
        vote = None
        try:
            claim = Claim.objects.get(pk=self.kwargs['pk'])
            vote = Vote.objects.get(claim=claim, user=self.request.user)
        except:
            pass

        context = dict({'claim': claim, 'vote': vote})

        return context

    def post(self, request, *args, **kwargs):
        """
        Users requesting payout
        """

        claim = get_object_or_404(Claim, pk=self.kwargs['pk'])

        try:
            if request.user == claim.user:
                if claim.payout_request():
                    messages.success(request, 'Your payout was sent')
                else:
                    messages.error(request, "Sorry please try later")
            else:
                messages.error(request,
                               "Sorry, this is not your payout to claim")

        except:
            messages.error(request, "Sorry please try later")

        return redirect(reverse('claim-status',
                                kwargs={'pk': claim.id}))

# List Views


class BidList(LoginRequiredMixin, TemplateView):
    """List of bids for the User
    """
    template_name = 'bid_list.html'

    def get_context_data(self, **kwargs):
        try:
            bids = Bid.objects.filter(user=self.request.user)
        except:
            bids = []

        return dict({'bids': bids}, )


class ClaimList(LoginRequiredMixin, TemplateView):
    """List of claims for the User
    """
    template_name = 'claim_list.html'

    def get_context_data(self, **kwargs):
        try:
            claims = Claim.objects.filter(user=self.request.user)
            voted_claims = Claim.objects.voted_on_by_user(self.request.user)
        except:
            claims = []
            voted_claims = []

        return dict({'claims': claims, 'voted_claims': voted_claims})


class VoteList(LoginRequiredMixin, TemplateView):
    """List of vote by a User
    """
    template_name = 'vote_list.html'

    def get_context_data(self, **kwargs):
        try:
            votes = Vote.objects.filter(user=self.request.user)
        except:
            votes = []

        return dict({'votes': votes})
