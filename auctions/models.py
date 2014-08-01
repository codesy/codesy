from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.ForeignKey(User)
    balanced_card_href = models.CharField(max_length=100)
    balanced_bank_account_href = models.CharField(max_length=100)


class Bid(models.Model):
    user = models.ForeignKey(User)
    url = models.URLField()
    ask = models.DecimalField(max_digits=6, decimal_places=2)
    offer = models.DecimalField(max_digits=6, decimal_places=2)
