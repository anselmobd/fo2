# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-04-03 20:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estoque', '0016_tipomovstq_renomeia'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tipomovstq',
            name='renomeia',
            field=models.BooleanField(default=False, verbose_name='Renomeia'),
        ),
    ]
