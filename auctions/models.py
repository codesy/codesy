from django.contrib.auth.models import User
from django.db import models


class Bid(models.Model):
    user = models.ForeignKey(User)
    url = models.URLField()
    ask = models.DecimalField(max_digits=6, decimal_places=2)
    offer = models.DecimalField(max_digits=6, decimal_places=2)
