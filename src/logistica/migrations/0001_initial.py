# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-07 10:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NotaFiscal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.IntegerField(unique=True)),
                ('ativa', models.BooleanField(default=True)),
                ('saida', models.DateField(blank=True, null=True)),
                ('entrega', models.DateField(blank=True, null=True)),
                ('confirmada', models.BooleanField(default=False)),
                ('observacao', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'fo2_fat_nf',
            },
        ),
    ]
