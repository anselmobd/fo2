# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-05-08 17:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lotes', '0022_lote_trail'),
    ]

    operations = [
        migrations.AddField(
            model_name='lote',
            name='estagio',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='lote',
            name='qtd',
            field=models.IntegerField(default=0, verbose_name='quantidade em produçao ou produzida'),
        ),
        migrations.AlterField(
            model_name='lote',
            name='qtd_produzir',
            field=models.IntegerField(verbose_name='quantidade a produzir'),
        ),
    ]
