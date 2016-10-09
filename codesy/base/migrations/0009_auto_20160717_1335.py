# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-07-17 13:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_auto_20160717_1216'),
    ]

    operations = [
        migrations.AddField(
            model_name='stripeaccount',
            name='public_key',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='stripeaccount',
            name='secret_key',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='stripeaccount',
            name='tos_acceptance_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='stripeaccount',
            name='tos_acceptance_ip',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
