# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0010_vote'),
    ]

    operations = [
        migrations.RenameField(
            model_name='claim',
            old_name='claimant',
            new_name='user',
        ),
        migrations.AlterUniqueTogether(
            name='claim',
            unique_together=set([('user', 'issue')]),
        ),
    ]
