# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-04-03 16:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estoque', '0014_tipomovstq_menu'),
    ]

    operations = [
        migrations.AddField(
            model_name='tipomovstq',
            name='ordem',
            field=models.IntegerField(default=0),
        ),
    ]
