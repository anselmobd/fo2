# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-07-15 19:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manutencao', '0021_rotinapasso_alter_verbose_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rotina',
            name='qtd_tempo',
        ),
        migrations.RemoveField(
            model_name='rotina',
            name='unidade_tempo',
        ),
    ]
