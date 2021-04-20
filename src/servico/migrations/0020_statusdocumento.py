# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-04-20 20:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servico', '0019_tipoevento_init_flags'),
    ]

    operations = [
        migrations.CreateModel(
            name='StatusDocumento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=20)),
                ('slug', models.SlugField()),
                ('criado', models.BooleanField(default=False)),
                ('cancelado', models.BooleanField(default=False)),
                ('iniciado', models.BooleanField(default=False)),
                ('terminado', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Status de documento',
                'verbose_name_plural': 'Status de documento',
                'db_table': 'fo2_serv_status_doc',
            },
        ),
    ]
