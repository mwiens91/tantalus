# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-11-20 00:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tantalus', '0075_auto_20181116_0012'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='generictaskinstance',
            name='host',
        ),
        migrations.RemoveField(
            model_name='generictaskinstance',
            name='task_type',
        ),
        migrations.RemoveField(
            model_name='generictasktype',
            name='default_host',
        ),
        migrations.DeleteModel(
            name='GenericTaskInstance',
        ),
        migrations.DeleteModel(
            name='GenericTaskType',
        ),
    ]
