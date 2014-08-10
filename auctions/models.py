from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User)
    balanced_card_href = models.CharField(max_length=100)
    balanced_bank_account_href = models.CharField(max_length=100)


class Bid(models.Model):
    user = models.ForeignKey(User)
    url = models.URLField()
    ask = models.DecimalField(max_digits=6, decimal_places=2)
    offer = models.DecimalField(max_digits=6, decimal_places=2)


@receiver(models.signals.post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
        if created and not kwargs.get('raw', False):
            p, created = Profile.objects.get_or_create(user=instance)
