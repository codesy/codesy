# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-08-06 19:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0032_auto_20160730_1539'),
    ]

    operations = [
        migrations.RenameField(
            model_name='offer',
            old_name='confirmation',
            new_name='charge_id',
        ),
        migrations.RenameField(
            model_name='payout',
            old_name='confirmation',
            new_name='charge_id',
        ),
        migrations.AddField(
            model_name='offer',
            name='refund_id',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='payout',
            name='refund_id',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
