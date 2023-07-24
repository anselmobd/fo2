# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def notafiscal_acerta_empresa(apps, schema_editor):
    NotaFiscal = apps.get_model(
        "logistica", "NotaFiscal")
    notas_fiscais = NotaFiscal.objects.all()
    for nota_fiscal in notas_fiscais:
        if nota_fiscal.numero < 10_000:
            nota_fiscal.empresa = 2
            nota_fiscal.save()


class Migration(migrations.Migration):

    dependencies = [
        ('logistica', '0051_notafiscal_empresa'),
    ]

    operations = [
        migrations.RunPython(notafiscal_acerta_empresa),
    ]
