# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-01-24 17:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0009_fo2_colaborador_persona'),
    ]

    operations = [
        migrations.AlterField(
            model_name='colaborador',
            name='obs',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
