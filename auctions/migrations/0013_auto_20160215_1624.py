# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0012_auto_20160215_1608'),
    ]

    operations = [
        migrations.AddField(
            model_name='bid',
            name='created',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='bid',
            name='modified',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
