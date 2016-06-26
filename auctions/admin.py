from django.contrib import admin

from .models import Bid, Issue, Claim, Vote, Offer, Payout, OfferFee, PayoutFee


class BidAdmin(admin.ModelAdmin):
    list_display = ('user', 'url', 'ask', 'offer')
    list_filter = ('user', 'url')


class ClaimAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'issue')
    list_filter = ('status', 'user')


admin.site.register(Bid, BidAdmin)
admin.site.register(Issue)
admin.site.register(Claim, ClaimAdmin)
admin.site.register(Vote)
admin.site.register(Offer)
admin.site.register(Payout)
admin.site.register(OfferFee)
admin.site.register(PayoutFee)
