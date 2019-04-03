# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def notafiscal_acerta_posicao_entregue(apps, schema_editor):
    NotaFiscal = apps.get_model(
        "logistica", "NotaFiscal")
    notas_fiscais = NotaFiscal.objects.all()
    for nota_fiscal in notas_fiscais:
        if nota_fiscal.confirmada:
            nota_fiscal.posicao_id = 5
            nota_fiscal.save()


def desfaz_notafiscal_acerta_posicao_entregue(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('logistica', '0022_notafiscal_acerta_posicao'),
    ]

    operations = [
        migrations.RunPython(
            notafiscal_acerta_posicao_entregue,
            desfaz_notafiscal_acerta_posicao_entregue),
    ]
