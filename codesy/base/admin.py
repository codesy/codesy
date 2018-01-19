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
        ('Accepted Terms',
            {'fields': ('tos_acceptance_ip', 'tos_acceptance_date')}),
        ('Stripe tokens',
            {'fields':
                ('stripe_card', 'stripe_customer', 'stripe_bank_account')
             }
         ),
        ('CC information',
            {'fields':
                ('card_brand', 'card_last4')
             }
         ),

    )
    list_display = ('username', 'email', 'is_active', 'date_joined',
                    'is_staff', 'stripe_customer', 'stripe_bank_account')
    list_filter = ('date_joined', 'is_active', 'is_staff', 'stripe_customer',
                   'stripe_bank_account')


admin.site.register(User, CodesyUserAdmin)
