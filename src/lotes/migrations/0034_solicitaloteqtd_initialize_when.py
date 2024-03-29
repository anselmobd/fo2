# -*- coding: utf-8 -*-
# Generated by Anselmo on 2019-06-12 10:36
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
        ('lotes', '0033_solicitaloteqtd_add_tablehead_fields'),
    ]

    operations = [
        migrations.RunPython(set_when, reverse_set_when),
        migrations.AlterField(
            model_name='solicitaloteqtd',
            name='when',
            field=models.DateTimeField(verbose_name='quando'),
        ),
    ]
