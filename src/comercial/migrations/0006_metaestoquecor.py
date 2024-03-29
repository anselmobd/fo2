# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-07-04 14:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0005_metaestoquetamanho'),
    ]

    operations = [
        migrations.CreateModel(
            name='MetaEstoqueCor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cor', models.CharField(max_length=6)),
                ('quantidade', models.IntegerField()),
                ('meta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='comercial.MetaEstoque')),
            ],
            options={
                'verbose_name': 'Grade de cores de meta de estoque',
                'db_table': 'fo2_meta_estoque_cor',
            },
        ),
    ]
