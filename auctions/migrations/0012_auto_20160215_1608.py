# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0011_auto_20160214_1622'),
    ]

    operations = [
        migrations.AlterField(
            model_name='claim',
            name='status',
            field=models.CharField(default=b'Pending', max_length=255, choices=[(b'Pending', b'Pending'), (b'Approved', b'Approved'), (b'Rejected', b'Rejected')]),
        ),
    ]
