# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-07-15 18:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('manutencao', '0017_fo2_man_periodo_loaddata'),
    ]

    operations = [
        migrations.AddField(
            model_name='rotina',
            name='periodo',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='manutencao.Periodo', verbose_name='Período'),
        ),
    ]
