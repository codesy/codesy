# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auctions', '0006_auto_20150103_1924'),
    ]

    operations = [
        migrations.CreateModel(
            name='Claim',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(null=True, blank=True)),
                ('modified', models.DateTimeField(auto_now=True, null=True)),
                ('status', models.CharField(default=b'OP', max_length=2, choices=[(None, b''), (b'OP', b'Open'), (b'ES', b'Escrow'), (b'PA', b'Paid'), (b'RE', b'Rejected')])),
                ('claimant', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('issue', models.ForeignKey(to='auctions.Issue')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
