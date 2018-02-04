import csv

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse

from .models import User


def download_user_csv(modeladmin, request, queryset):
    if not request.user.is_staff:
        raise PermissionDenied

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename=users.csv'

    writer = csv.writer(response)
    field_names = ['username', 'first_name', 'last_name', 'email']
    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])
    return response


download_user_csv.short_description = "Download CSV"


class CodesyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class CodesyUserAdmin(UserAdmin):
    actions = [download_user_csv]
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
