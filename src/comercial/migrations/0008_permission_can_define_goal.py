# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-07-05 10:39
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0007_metaestoque_meta_estoque'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='metaestoque',
            options={'permissions': (('can_define_goal', 'Can define goal'),), 'verbose_name': 'Parametros para meta de estoque'},
        ),
    ]
