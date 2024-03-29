# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-06-11 20:05
from __future__ import unicode_literals

from django.db import migrations, models


def set_when(apps, schema_editor):
    SLQ = apps.get_model('lotes', 'SolicitaLoteQtd')
    for slq in SLQ.objects.all().iterator():
        slq.when = slq.update_at
        slq.save()


def reverse_set_when(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('lotes', '0032_auto_20190328_1053'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitaloteqtd',
            name='deleted',
            field=models.NullBooleanField(default=False, verbose_name='apagado'),
        ),
        migrations.AddField(
            model_name='solicitaloteqtd',
            name='origin_id',
            field=models.IntegerField(default=0, verbose_name='id de origem'),
        ),
        migrations.AddField(
            model_name='solicitaloteqtd',
            name='unique_aux',
            field=models.IntegerField(default=0, verbose_name='campo auxiliar para unique_together'),
        ),
        migrations.AddField(
            model_name='solicitaloteqtd',
            name='version',
            field=models.IntegerField(default=0, verbose_name='versão'),
        ),
        migrations.AddField(
            model_name='solicitaloteqtd',
            name='when',
            field=models.DateTimeField(blank=True, null=True, verbose_name='quando'),
        ),
        # migrations.RunPython(set_when, reverse_set_when),
        # migrations.AlterField(
        #     model_name='solicitaloteqtd',
        #     name='when',
        #     field=models.DateTimeField(verbose_name='quando'),
        # ),
    ]
