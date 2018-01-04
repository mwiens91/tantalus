# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-04 19:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tantalus', '0023_auto_20180104_1909'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bamfile',
            name='bam_index_file',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bam_index_file', to='tantalus.FileResource'),
        ),
    ]
