# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-08-09 18:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lotes', '0039_regraleadtamanho'),
    ]

    operations = [
        migrations.AddField(
            model_name='regraleadtamanho',
            name='ordem_tamanho',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='Ordem do tamanho'),
        ),
    ]
