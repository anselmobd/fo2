# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-03-27 15:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produto', '0025_produto_nivel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produto',
            name='nivel',
            field=models.IntegerField(db_index=True, verbose_name='Nível'),
        ),
    ]
