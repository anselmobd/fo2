# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-07-12 19:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manutencao', '0007_maquina_data_inicio'),
    ]

    operations = [
        migrations.CreateModel(
            name='Atividade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resumo', models.CharField(db_index=True, max_length=100)),
                ('descricao', models.CharField(max_length=250, verbose_name='Descrição')),
            ],
            options={
                'verbose_name': 'Atividade',
                'db_table': 'fo2_man_atividade',
            },
        ),
    ]
