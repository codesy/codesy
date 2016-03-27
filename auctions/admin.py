from django.contrib import admin

from .models import Bid, Issue, Claim, Vote, Offer, Payout

admin.site.register(Bid)
admin.site.register(Issue)
admin.site.register(Claim)
admin.site.register(Vote)
admin.site.register(Offer)
admin.site.register(Payout)
