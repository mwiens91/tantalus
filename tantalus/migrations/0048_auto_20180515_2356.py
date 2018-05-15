# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-05-15 23:56
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations
import tantalus.generictask_models


class Migration(migrations.Migration):

    dependencies = [
        ('tantalus', '0047_auto_20180515_2352'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generictasktype',
            name='required_and_default_args',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=tantalus.generictask_models.return_gen_task_type_arg_default, help_text=b"The arguments that the task requires as a JSON object. Looking at the object as a dictionary, the keys are the argument names and the corresponding values are the default values for these arguments. To specify an argument with no default value, simply use 'null' (without the quotes) as its value.", null=True, verbose_name=b'script arguments'),
        ),
    ]
