from django.contrib import admin

from .models import Bid, Issue, Claim, Vote, Offer, Payout, OfferFee, PayoutFee

admin.site.register(Bid)
admin.site.register(Issue)
admin.site.register(Claim)
admin.site.register(Vote)
admin.site.register(Offer)
admin.site.register(Payout)
admin.site.register(OfferFee)
admin.site.register(PayoutFee)
