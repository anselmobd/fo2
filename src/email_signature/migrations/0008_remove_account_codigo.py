# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-02-06 23:49
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('email_signature', '0007_account_alter_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='codigo',
        ),
    ]
