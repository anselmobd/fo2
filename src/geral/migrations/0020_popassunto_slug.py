# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-01-22 21:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geral', '0019_pop_assunto'),
    ]

    operations = [
        migrations.AddField(
            model_name='popassunto',
            name='slug',
            field=models.SlugField(default='slug'),
        ),
    ]
