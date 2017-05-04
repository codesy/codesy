from decimal import Decimal
from urlparse import urldefrag

from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import messages

from auctions.models import Bid, Claim, Vote

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class AddonLogin (TemplateView):
    template_name = 'addon/logon.html'


class BidStatusView(UserPassesTestMixin, LoginRequiredMixin, TemplateView):
    """
    Requests for /bid/?url= will receive the HTML form for creating a bid (if
    none exists) or updating the user's existing bid.

    url -- url of an OSS issue or bug
    """
    login_url = '/addon-login/'
    template_name = "addon/bidders.html"

    def test_func(self):
        if self.request.user.is_active:
            if not self.request.user.stripe_customer:
                self.template_name = "addon/register_card.html"
            return True
        return False

    def _get_bid(self, url):
        try:
            return Bid.objects.get(user=self.request.user, url=url)
        except:
            return None

    def _url_path_only(self, url):
        return urldefrag(url)[0]

    def get_context_data(self, **kwargs):
        url = self._url_path_only(self.request.GET['url'])
        bid = self._get_bid(url)
        if bid is None:
            return dict({'bid': bid, 'url': url})

        # rejected claims should be ignored so new claims can be made
        claims = (
            Claim.objects.filter(issue=bid.issue).exclude(status='Rejected'))

        users_claims = claims.filter(
            user=self.request.user).order_by('modified')

        if users_claims:
            self.template_name = 'addon/claimaint.html'
            return dict({'claim': users_claims[0]})
        if claims:
            if bid.offer:
                self.template_name = 'addon/voters.html'
            else:
                self.template_name = 'addon/bid_closed.html'
            return dict({'claims': claims})
        else:
            return dict({'bid': bid, 'url': url})

    def post(self, *args, **kwargs):
        """
        Save changes to bid and get payment for offer
        """
        url = self._url_path_only(self.request.POST['url'])
        ask_amount = self.request.POST['ask']
        offer_amount = self.request.POST['offer']

        bid = self._get_bid(url)
        if bid is None:
            bid = Bid(user=self.request.user, url=url)

        if ask_amount:
            bid.ask = ask_amount
            bid.save()
            messages.success(self.request, "Thanks for the ask!")

        if (
            offer_amount and
            Decimal(offer_amount) > 0.0 and
            Decimal(offer_amount) != bid.offer
        ):
            new_offer = bid.set_offer(offer_amount)
            if new_offer.error_message:
                messages.error(self.request, new_offer.error_message)
            else:
                messages.success(self.request, "Thanks for the offer!")

        return redirect("%s?url=%s" % (reverse('bid-status'), url))


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
        payout_totals = {'fees': 0, 'credits': 0, 'final_payout': 0}
        claim = get_object_or_404(Claim, pk=self.kwargs['pk'])
        try:
            for payout in claim.successful_payouts().all():
                for credit in payout.credits():
                    payout_totals['credits'] += payout.amount
                for fee in payout.fees():
                    payout_totals['fees'] += fee.amount
                payout_totals['final_payout'] += payout.charge_amount

            vote = Vote.objects.get(claim=claim, user=self.request.user)
        except:
            pass
        context = dict({
            'claim': claim,
            'vote': vote,
            'payout_totals': payout_totals
        })
        return context

    def post(self, request, *args, **kwargs):
        """
        Users requesting payout
        """

        claim = get_object_or_404(Claim, pk=self.kwargs['pk'])

        if request.user != claim.user:
            messages.error(
                request,
                "Sorry, this is not your payout to claim"
            )
            return redirect(reverse('claim-status',
                            kwargs={'pk': claim.id}))

        if claim.payout():
            messages.success(request, 'Your payout was sent.')
        else:
            messages.error(
                request, "Sorry please try this payout later")

        return redirect(reverse('claim-status',
                                kwargs={'pk': claim.id}))


# List Views
class BidList(LoginRequiredMixin, TemplateView):
    """List of bids for the User
    """
    template_name = 'bid_list.html'

    def get_context_data(self, **kwargs):
        try:
            bids = (Bid.objects.filter(user=self.request.user)
                    .order_by('-created'))
        except:
            bids = []

        return dict({'bids': bids}, )


class ClaimList(LoginRequiredMixin, TemplateView):
    """List of claims for the User
    """
    template_name = 'claim_list.html'

    def get_context_data(self, **kwargs):
        try:
            claims = (Claim.objects.filter(user=self.request.user)
                      .order_by('-created'))
            voted_claims = (Claim.objects.voted_on_by_user(self.request.user)
                            .order_by('-created'))
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
            votes = (Vote.objects.filter(user=self.request.user)
                     .order_by('-created'))
        except:
            votes = []

        return dict({'votes': votes})
