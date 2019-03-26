# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def notafiscal_acerta_posicao(apps, schema_editor):
    NotaFiscal = apps.get_model(
        "logistica", "NotaFiscal")
    notas_fiscais = NotaFiscal.objects.all()
    for nota_fiscal in notas_fiscais:
        if nota_fiscal.saida is not None:
            nota_fiscal.posicao_id = 3
            nota_fiscal.save()


def desfaz_notafiscal_acerta_posicao(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('logistica', '0021_posicaocargaalteracaolog'),
    ]

    operations = [
        migrations.RunPython(
            notafiscal_acerta_posicao,
            desfaz_notafiscal_acerta_posicao),
    ]
