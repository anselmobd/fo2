# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-07-05 13:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0008_permission_can_define_goal'),
    ]

    operations = [
        migrations.AddField(
            model_name='metaestoquetamanho',
            name='ordem',
            field=models.IntegerField(default=0),
        ),
    ]
