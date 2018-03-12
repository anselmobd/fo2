# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-03-12 21:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geral', '0013_auto_20180123_1410'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descricao', models.CharField(blank=True, max_length=255, verbose_name='título')),
                ('pop', models.FileField(upload_to='pop/', verbose_name='Arquivo POP')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('habilitado', models.NullBooleanField(default=True)),
            ],
        ),
    ]
