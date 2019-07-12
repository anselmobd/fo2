# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-07-12 19:04
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('manutencao', '0005_maquina'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsuarioTipoMaquina',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_maquina', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manutencao.TipoMaquina', verbose_name='Tipo de máquina')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='usuário')),
            ],
            options={
                'verbose_name': 'Usuário/Tipo de máquina',
                'verbose_name_plural': 'Usuários/Tipos de máquinas',
                'db_table': 'fo2_man_user_tipo_maq',
            },
        ),
        migrations.AlterUniqueTogether(
            name='usuariotipomaquina',
            unique_together=set([('usuario', 'tipo_maquina')]),
        ),
    ]
