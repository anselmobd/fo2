# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-07-07 17:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lotes', '0054_can_print_parciais'),
    ]

    operations = [
        migrations.AddField(
            model_name='lote',
            name='conserto',
            field=models.IntegerField(default=0, verbose_name='quantidade em conserto'),
        ),
    ]
