# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-04-19 11:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lotes', '0017_lote_local_at'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lote',
            options={'permissions': (('can_inventorize_lote', 'Can inventorize lote'),), 'verbose_name': 'lote'},
        ),
    ]
