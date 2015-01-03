# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_auto_20150103_0221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bid',
            name='ask',
            field=models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='bid',
            name='offer',
            field=models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True),
            preserve_default=True,
        ),
    ]
