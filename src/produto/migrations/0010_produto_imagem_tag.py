# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-11-27 20:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_imagemtag'),
        ('produto', '0009_produtocor__composicao'),
    ]

    operations = [
        migrations.AddField(
            model_name='produto',
            name='imagem_tag',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.ImagemTag', verbose_name='Imagem do TAG'),
        ),
    ]
