# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-04-21 19:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servico', '0031_tipoevento_to_evento'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='evento',
            options={'verbose_name': 'Evento'},
        ),
        migrations.AlterModelTable(
            name='evento',
            table='fo2_serv_evento',
        ),
    ]
