# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-06-03 12:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('estoque', '0021_movstq_obs'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='estoquepermissions',
            options={'managed': False, 'permissions': (('can_transferencia', 'Pode fazer transferência entre depósitos'),), 'verbose_name': 'Permissões de estoque'},
        ),
    ]
