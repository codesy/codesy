from django.contrib import admin
from payments.models import StripeAccount, StripeEvent


admin.site.register(StripeAccount)
admin.site.register(StripeEvent)
