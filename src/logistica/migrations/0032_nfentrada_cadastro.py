# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-06-14 20:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistica', '0031_nfentrada_numero'),
    ]

    operations = [
        migrations.AddField(
            model_name='nfentrada',
            name='cadastro',
            field=models.CharField(default='', max_length=20),
        ),
    ]
