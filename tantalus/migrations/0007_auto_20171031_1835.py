# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-31 18:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tantalus', '0006_auto_20171031_1818'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileinstance',
            name='filename_override',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
        migrations.AlterField(
            model_name='historicalfileinstance',
            name='filename_override',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
    ]
