# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-07-12 18:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TipoMaquina',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(db_index=True, max_length=20)),
                ('slug', models.SlugField()),
                ('descricao', models.CharField(max_length=250, verbose_name='Descrição')),
            ],
            options={
                'verbose_name': 'Tipo de máquina',
                'verbose_name_plural': 'Tipos de máquinas',
                'db_table': 'fo2_man_tipo_maquina',
            },
        ),
    ]
