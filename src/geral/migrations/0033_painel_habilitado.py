# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-05-17 19:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geral', '0032_config_usuario'),
    ]

    operations = [
        migrations.AddField(
            model_name='painel',
            name='habilitado',
            field=models.NullBooleanField(default=True),
        ),
    ]
