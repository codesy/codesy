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
    template_name = "addon/bid.html"

    def test_func(self):
        return self.request.user.is_active


    def _get_bid(self, url):
        try:
            return Bid.objects.get(user=self.request.user, url=url)
        except:
            new_bid = Bid(user=self.request.user, url=url)
            new_bid.save()
            return new_bid

    def get_context_data(self, **kwargs):
        url = self.request.GET['url']
        bid = self._get_bid(url)
        # rejected claims should be ignored so new claims can be made
        claims = Claim.objects.filter(issue=bid.issue).exclude(status='Rejected')

        if claims.filter(user=self.request.user):
            self.template_name = 'addon/claimaint.html'
            return dict({'bid': bid, 'url': url, 'claim': claims[0]})

        elif some_test_for_:
            self.template_name = 'addon/voters.html'
            return dict({'bid': bid, 'url': url, 'claims': claims})

        else:
            self.template_name = 'addon/bystanders.html'
            return dict({'bid': bid, 'url': url, 'claim': claims[0]})


    def post(self, *args, **kwargs):
        """
        Save changes to bid and get payment for offer
        """
        url = self.request.POST['url']
        new_ask_amount = self.request.POST['ask']
        new_offer_amount = self.request.POST['offer']

        bid = self._get_bid(url)

        if new_ask_amount:
            bid.ask = new_ask_amount
            bid.save()

        if new_offer_amount:
            new_offer = bid.set_offer(new_offer_amount)
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
        total_payout = {'total': 0,
                        'fees': {'codesy': 0, 'Stripe': 0},
                        'credits': {'surplus': 0}
                        }
        try:
            claim = Claim.objects.get(pk=self.kwargs['pk'])
            for payout in claim.successful_payouts().all():
                total_payout['total'] += payout.charge_amount
                for fee in payout.fees():
                    total_payout['fees'][fee.fee_type] += fee.amount
                for credit in payout.credits():
                    total_payout['credits'][credit.fee_type] += credit.amount
            vote = Vote.objects.get(claim=claim, user=self.request.user)
        except:
            pass
        context = dict({
            'claim': claim,
            'vote': vote,
            'aggregate_payout': total_payout
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
