# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0008_auto_20150301_1953'),
    ]

    operations = [
        migrations.AddField(
            model_name='claim',
            name='evidence',
            field=models.URLField(blank=True),
            preserve_default=True,
        ),
    ]
