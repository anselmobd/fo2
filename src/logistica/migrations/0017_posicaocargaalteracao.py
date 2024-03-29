# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-03-25 15:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('logistica', '0016_rotinalogistica_loaddata'),
    ]

    operations = [
        migrations.CreateModel(
            name='PosicaoCargaAlteracao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordem', models.IntegerField(default=0)),
                ('descricao', models.CharField(max_length=200, verbose_name='descrição')),
                ('efeito', models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='logistica.RotinaLogistica')),
                ('final', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='posicao_final_set', to='logistica.PosicaoCarga', verbose_name='Estado Final')),
                ('inicial', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='posicao_inicial_set', to='logistica.PosicaoCarga', verbose_name='Estado inicial')),
            ],
            options={
                'verbose_name': 'Alteração de posição de carga(NF)',
                'verbose_name_plural': 'Alterações de Posição de carga(NF)',
                'db_table': 'fo2_pos_carga_alt',
            },
        ),
    ]
