from django.contrib import admin

from .models import Bid, Issue, Claim, Vote

admin.site.register(Bid)
admin.site.register(Issue)
admin.site.register(Claim)
admin.site.register(Vote)
