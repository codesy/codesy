# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-08 12:16
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0025_auto_20160408_1206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='transaction_key',
            field=models.CharField(blank=True, default=uuid.uuid4, max_length=255),
        ),
        migrations.AlterField(
            model_name='payout',
            name='transaction_key',
            field=models.CharField(blank=True, default=uuid.uuid4, max_length=255),
        ),
    ]
