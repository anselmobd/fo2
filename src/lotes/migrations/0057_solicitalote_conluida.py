# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-10-09 12:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lotes', '0056_solicitalote_coleta'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitalote',
            name='conluida',
            field=models.BooleanField(default=False, verbose_name='Solicitação concluída'),
        ),
    ]
