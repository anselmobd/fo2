# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-08-27 17:33
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('manutencao', '0024_fo2_man_rotina_passo_loaddata_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='OS',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.IntegerField(default=0, verbose_name='número')),
                ('data_agendada', models.DateField(verbose_name='Data agendada')),
                ('maquina', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manutencao.Maquina', verbose_name='máquina')),
                ('rotina', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manutencao.Rotina')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='usuário')),
            ],
            options={
                'verbose_name': 'OS de rotina de manutenção',
                'verbose_name_plural': 'OSs de rotinas de manutenção',
                'db_table': 'fo2_man_os',
            },
        ),
    ]
