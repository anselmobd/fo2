# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-05-19 21:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lotes', '0077_regracolecao_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='regracolecao',
            name='lotes_caixa',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
