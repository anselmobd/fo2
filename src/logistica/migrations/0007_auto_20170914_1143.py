# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-14 14:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistica', '0006_auto_20170712_1001'),
    ]

    operations = [
        migrations.AddField(
            model_name='notafiscal',
            name='valor',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='notafiscal',
            name='volumes',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
