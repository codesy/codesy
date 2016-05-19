from django.db import models


class ClaimManager(models.Manager):
    def voted_on_by_user(self, user):
        return super(ClaimManager, self).get_queryset().filter(
            vote__user=user
        )
