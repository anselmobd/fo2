# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-12-22 19:03
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ti', '0008_interface_type'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='equipamento',
            table='fo2_ti_equipment',
        ),
    ]
