# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-07-12 18:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('manutencao', '0004_fo2_man_unidade_tempo_loaddata'),
    ]

    operations = [
        migrations.CreateModel(
            name='Maquina',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(db_index=True, max_length=50)),
                ('slug', models.SlugField()),
                ('descricao', models.CharField(max_length=250, verbose_name='Descrição')),
                ('tipo_maquina', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manutencao.TipoMaquina', verbose_name='Tipo de máquina')),
            ],
            options={
                'verbose_name': 'Máquina',
                'db_table': 'fo2_man_maquina',
            },
        ),
    ]
