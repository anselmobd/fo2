# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-05-10 17:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistica', '0025_0025_fo2_fat_nf__natu_venda__index'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notafiscal',
            name='ativa',
            field=models.BooleanField(db_index=True, default=True),
        ),
    ]
