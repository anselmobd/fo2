# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-04-21 19:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servico', '0033_evento_slug_to_codigo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evento',
            name='codigo',
            field=models.CharField(max_length=20),
        ),
    ]
