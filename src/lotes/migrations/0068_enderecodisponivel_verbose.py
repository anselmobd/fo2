# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-12-17 14:20
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lotes', '0067_lote_sync'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='enderecodisponivel',
            options={'verbose_name': 'Endereço disponível', 'verbose_name_plural': 'Endereços disponíveis'},
        ),
    ]
