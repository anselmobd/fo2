# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-05-15 17:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('geral', '0029_parametro'),
    ]

    operations = [
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.CharField(max_length=255)),
                ('parametro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='geral.Parametro')),
            ],
            options={
                'verbose_name': 'Configuração',
                'verbose_name_plural': 'Configurações',
                'db_table': 'fo2_config',
            },
        ),
    ]
