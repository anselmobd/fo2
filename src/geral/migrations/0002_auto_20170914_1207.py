# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-14 15:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geral', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recordtracking',
            name='user',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='Usuário'),
        ),
    ]
