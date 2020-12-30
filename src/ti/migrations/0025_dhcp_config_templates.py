# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-12-30 20:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ti', '0024_interface_dhcp_config'),
    ]

    operations = [
        migrations.AddField(
            model_name='dhcpconfig',
            name='primary_template',
            field=models.CharField(blank=True, max_length=65535, null=True, verbose_name='Gabarito para o servidor primário (ou único)'),
        ),
        migrations.AddField(
            model_name='dhcpconfig',
            name='secondary_template',
            field=models.CharField(blank=True, max_length=65535, null=True, verbose_name='Gabarito para o servidor secundário'),
        ),
    ]
