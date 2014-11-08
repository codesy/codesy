from django.conf import settings
from django.db import models


class Bid(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    url = models.URLField()
    ask = models.DecimalField(max_digits=6, decimal_places=2)
    offer = models.DecimalField(max_digits=6, decimal_places=2)
