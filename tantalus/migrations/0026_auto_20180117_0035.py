# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-17 00:35
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tantalus', '0025_auto_20180111_2207'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gscwgsbamquery',
            name='sample',
        ),
        migrations.AddField(
            model_name='gscwgsbamquery',
            name='library_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50), default=[], size=None),
            preserve_default=False,
        ),
    ]
