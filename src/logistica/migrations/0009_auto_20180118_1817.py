# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-18 20:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistica', '0008_auto_20170914_1207'),
    ]

    operations = [
        migrations.AddField(
            model_name='notafiscal',
            name='ped_cliente',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='pedido cliente'),
        ),
        migrations.AddField(
            model_name='notafiscal',
            name='pedido',
            field=models.IntegerField(blank=True, null=True, verbose_name='pedido'),
        ),
    ]
