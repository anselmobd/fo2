# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-14 15:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistica', '0007_auto_20170914_1143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notafiscal',
            name='confirmada',
            field=models.BooleanField(default=False, verbose_name='entregue'),
        ),
        migrations.AlterField(
            model_name='notafiscal',
            name='entrega',
            field=models.DateField(blank=True, null=True, verbose_name='agendamento'),
        ),
    ]
