from django.contrib import admin
from .models import StripeAccount, StripeEvent


class StripeAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_id', 'available_balance',)

    readonly_fields = (
        'user', 'public_key', 'available_balance',
    )


class StripeEventAdmin(admin.ModelAdmin):
    list_display = (
        'event_id', 'type', 'created', 'verified', 'processed', 'user_id')
    search_fields = ['message_text']

    readonly_fields = (
        'user_id', 'type', 'created', 'event_id', 'verified',
        'processed', 'message_text',)

admin.site.register(StripeAccount, StripeAccountAdmin)
admin.site.register(StripeEvent, StripeEventAdmin)
