# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-05-19 20:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lotes', '0074_regracolecao_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='regracolecao',
            name='colecao',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='Coleção'),
        ),
        migrations.AlterField(
            model_name='regracolecao',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
