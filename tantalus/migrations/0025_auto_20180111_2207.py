# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-11 22:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tantalus', '0024_auto_20180104_1932'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalserverstorage',
            name='read_only',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='serverstorage',
            name='read_only',
            field=models.BooleanField(default=True),
        ),
    ]
