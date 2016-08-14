from django.contrib import admin
from .models import StripeAccount, StripeEvent


class StripeEventAdmin(admin.ModelAdmin):
    list_display = ('type', 'processed')
    list_filter = ('event_id',)
    search_fields = ['event_id']


admin.site.register(StripeAccount)
admin.site.register(StripeEvent, StripeEventAdmin)
