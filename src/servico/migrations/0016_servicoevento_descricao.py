# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-04-14 18:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servico', '0015_servicoevento_ajustes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicoevento',
            name='descricao',
            field=models.TextField(default='', max_length=2000, verbose_name='Descrição'),
        ),
    ]
