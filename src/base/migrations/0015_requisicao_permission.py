# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-05-13 17:41
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0014_requisicao'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='requisicao',
            options={'permissions': (('can_visualize_usage_log', 'Can visualize usage log'),), 'verbose_name': 'Requisição', 'verbose_name_plural': 'Requisições'},
        ),
    ]
