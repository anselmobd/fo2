# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-03-19 14:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistica', '0011_notafiscal_trail'),
    ]

    operations = [
        migrations.AddField(
            model_name='notafiscal',
            name='nf_devolucao',
            field=models.IntegerField(blank=True, null=True, verbose_name='Devolução'),
        ),
    ]
