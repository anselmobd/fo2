# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-11-24 13:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lotes', '0064_enderecodisponivel'),
    ]

    operations = [
        migrations.CreateModel(
            name='SolicitaLotePedido',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pedido', models.IntegerField()),
                ('solicitacao', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='lotes.SolicitaLote', verbose_name='Solicitação')),
            ],
            options={
                'verbose_name': 'Pedido de solicitação de lote',
                'db_table': 'fo2_cd_solicita_lote_pedido',
            },
        ),
    ]
