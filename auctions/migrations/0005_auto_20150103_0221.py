# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_auto_20141227_1923'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='bid',
            unique_together=set([('user', 'url')]),
        ),
    ]
