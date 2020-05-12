# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-05-12 13:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0013_colaborador_ip_interno'),
    ]

    operations = [
        migrations.CreateModel(
            name='Requisicao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_method', models.CharField(max_length=10, verbose_name='Tipo de requisição')),
                ('path_info', models.CharField(max_length=254, verbose_name='Endereço')),
                ('http_accept', models.CharField(max_length=254, verbose_name='HTTP Accept')),
                ('quando', models.DateTimeField(blank=True, null=True)),
                ('ip', models.CharField(max_length=47, verbose_name='IP')),
                ('colaborador', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base.Colaborador')),
            ],
            options={
                'verbose_name': 'Requisição',
                'verbose_name_plural': 'Requisições',
                'db_table': 'fo2_requisicao',
            },
        ),
    ]
