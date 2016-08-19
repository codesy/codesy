import json

from django.contrib import admin
from .models import StripeAccount, StripeEvent


class StripeAccountAdmin(admin.ModelAdmin):

    readonly_fields = (
        'user', 'account_id', 'secret_key', 'public_key',
        'available_balance'
    )


class StripeEventAdmin(admin.ModelAdmin):
    list_display = (
        'event_id', 'type', 'created', 'verified', 'processed', 'user_id')
    search_fields = ['message_text']

    readonly_fields = (
        'type', 'created', 'event_id', 'processed', 'message_text',)

    def message_text(self, instance):
        # Convert the data to sorted, indented JSON
        response = json.dumps(instance.message_text, sort_keys=True, indent=2)
        return response

admin.site.register(StripeAccount, StripeAccountAdmin)
admin.site.register(StripeEvent, StripeEventAdmin)
