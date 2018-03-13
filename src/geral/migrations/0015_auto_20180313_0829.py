# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-03-13 11:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geral', '0014_pop'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pop',
            options={'permissions': (('can_manage_pop', 'Can manage pop'),)},
        ),
        migrations.AlterField(
            model_name='pop',
            name='uploaded_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Inserido em'),
        ),
    ]
