from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    balanced_card_href = models.CharField(max_length=100, blank=True)
    balanced_bank_account_href = models.CharField(max_length=100, blank=True)

    USERNAME_FIELD = 'username'
