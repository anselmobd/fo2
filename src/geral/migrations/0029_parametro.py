# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-05-15 16:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('geral', '0028_tipoparametro_verbosename'),
    ]

    operations = [
        migrations.CreateModel(
            name='Parametro',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=25, unique=True, verbose_name='código')),
                ('descricao', models.CharField(max_length=255, unique=True, verbose_name='descrição')),
                ('ajuda', models.CharField(max_length=65535)),
                ('habilitado', models.NullBooleanField(default=True)),
                ('usuario', models.NullBooleanField(default=True, verbose_name='usuário')),
                ('tipo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='geral.TipoParametro')),
            ],
            options={
                'verbose_name': 'Parâmetro',
                'db_table': 'fo2_parametro',
            },
        ),
    ]
