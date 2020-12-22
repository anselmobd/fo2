# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-12-22 19:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ti', '0016_interface_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='EquipmentInterface',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('equipment', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ti.Equipment', verbose_name='Equipmento')),
                ('interface', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ti.Interface')),
            ],
            options={
                'db_table': 'fo2_ti_equipment_interface',
            },
        ),
    ]
