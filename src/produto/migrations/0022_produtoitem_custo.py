# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-04-29 19:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produto', '0021_produtotamanho_descricao'),
    ]

    operations = [
        migrations.AddField(
            model_name='produtoitem',
            name='custo',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True),
        ),
    ]
