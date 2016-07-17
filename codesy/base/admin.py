from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm

from .models import User, StripeAccount


class CodesyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class CodesyUserAdmin(UserAdmin):
    form = CodesyUserChangeForm

    fieldsets = UserAdmin.fieldsets + (
        ('Payments', {'fields': ('stripe_customer_token',)}),
    )

admin.site.register(User, CodesyUserAdmin)
admin.site.register(StripeAccount)
