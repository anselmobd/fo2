# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-07-04 14:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0003_modelopassadoperiodo'),
    ]

    operations = [
        migrations.CreateModel(
            name='MetaEstoque',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modelo', models.CharField(max_length=5)),
                ('data', models.DateField()),
                ('venda_mensal', models.IntegerField()),
                ('multiplicador', models.FloatField()),
            ],
            options={
                'verbose_name': 'Parametros para meta de estoque',
                'db_table': 'fo2_meta_estoque',
            },
        ),
    ]
