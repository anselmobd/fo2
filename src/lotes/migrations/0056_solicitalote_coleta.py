# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-10-06 16:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lotes', '0055_lote_conserto'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitalote',
            name='coleta',
            field=models.BooleanField(default=False, verbose_name='Pode coletar'),
        ),
    ]
