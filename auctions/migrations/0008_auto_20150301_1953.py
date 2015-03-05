# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0007_claim'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='claim',
            unique_together=set([('claimant', 'issue')]),
        ),
    ]
