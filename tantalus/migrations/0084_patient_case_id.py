# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-12-12 01:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tantalus', '0083_auto_20181206_1704'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='case_id',
            field=models.CharField(max_length=120, null=True),
        ),
    ]
