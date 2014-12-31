# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_bid_ask_match_sent'),
    ]

    operations = [
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField(unique=True, db_index=True)),
                ('state', models.CharField(max_length=255)),
                ('last_fetched', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='bid',
            name='issue',
            field=models.ForeignKey(to='auctions.Issue', null=True),
            preserve_default=True,
        ),
    ]
