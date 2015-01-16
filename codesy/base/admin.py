from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm

from .models import User


class CodesyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class CodesyUserAdmin(UserAdmin):
    form = CodesyUserChangeForm

    fieldsets = UserAdmin.fieldsets + (
        ('Payments', {'fields': ('balanced_card_href',
                                 'balanced_bank_account_href')}),
    )

admin.site.register(User, CodesyUserAdmin)
