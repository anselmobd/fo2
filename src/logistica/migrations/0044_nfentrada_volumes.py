# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-06-24 10:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistica', '0043_nfentrada_qtd_to_volumes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nfentrada',
            name='volumes',
            field=models.IntegerField(),
        ),
    ]
