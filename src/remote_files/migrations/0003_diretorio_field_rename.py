# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-02-07 19:10
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('remote_files', '0002_diretorio'),
    ]

    operations = [
        migrations.RenameField(
            model_name='diretorio',
            old_name='file_usuer',
            new_name='file_user',
        ),
    ]
