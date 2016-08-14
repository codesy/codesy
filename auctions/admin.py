from django.contrib import admin

from .models import (Bid, Claim, Issue, Offer, OfferFee, Payout,
                     PayoutCredit, PayoutFee, Vote)


class BidAdmin(admin.ModelAdmin):
    list_display = ('user', 'url', 'ask', 'offer')
    list_filter = ('ask_match_sent',)
    search_fields = ['user__username', 'user__email', 'title']


class IssueAdmin(admin.ModelAdmin):
    list_display = ('url', 'state', 'last_fetched')
    list_filter = ('state',)
    search_fields = ['title']


class ClaimAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'issue')
    list_filter = ('status',)
    search_fields = ['user__username', 'user__email', 'issue__url',
                     'issue__title']


class OfferAdmin(admin.ModelAdmin):
    list_display = ('user', 'bid', 'amount', 'charge_amount', 'refund_id',
                    'created')
    list_filter = ('api_success',)
    search_fields = ['bid__user__username', 'bid__user__email',
                     'error_message', 'confirmation', 'transaction_key']


class PayoutAdmin(admin.ModelAdmin):
    list_display = ('user', 'claim', 'amount', 'charge_amount', 'api_success',
                    'created')
    list_filter = ('api_success',)
    search_fields = ['claim__user__username', 'claim__user__email',
                     'confirmation', 'transaction_key']


class VoteAdmin(admin.ModelAdmin):
    list_display = ('claim', 'user', 'approved', 'created')
    list_filter = ('approved',)


class PayoutCreditAdmin(admin.ModelAdmin):
    list_display = ('payout', 'fee_type', 'amount', 'description')
    search_fields = ['description']


class PayoutFeeAdmin(admin.ModelAdmin):
    list_display = ('payout', 'fee_type', 'amount', 'description')
    search_fields = ['description']


class OfferFeeAdmin(admin.ModelAdmin):
    list_display = ('offer', 'fee_type', 'amount', 'description')
    search_fields = ['description']

admin.site.register(Bid, BidAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Claim, ClaimAdmin)
admin.site.register(Vote, VoteAdmin)
admin.site.register(Offer, OfferAdmin)
admin.site.register(Payout, PayoutAdmin)
admin.site.register(OfferFee, OfferFeeAdmin)
admin.site.register(PayoutFee, PayoutFeeAdmin)
admin.site.register(PayoutCredit, PayoutCreditAdmin)
