# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from pprint import pprint

from django.db import migrations


def alt_flags(tipoevento, slug, criar, inativar, ativar, edita_nivel, edita_equipe, edita_descricao):
    evento = tipoevento.objects.get(slug=slug)
    evento.criar = criar
    evento.inativar = inativar
    evento.ativar = ativar
    evento.edita_nivel = edita_nivel
    evento.edita_equipe = edita_equipe
    evento.edita_descricao = edita_descricao
    evento.save()


def init_flags(apps, schema_editor):
    tipoevento = apps.get_model("servico", "TipoEvento")

    alt_flags(tipoevento, 'req', True,  False, False, True,  True,  True)
    alt_flags(tipoevento, 'can', False, True,  False, False, False, True)
    alt_flags(tipoevento, 'rea', False, False, True,  True,  True,  True)
    alt_flags(tipoevento, 'alt', False, False, False, True,  True,  True)
    alt_flags(tipoevento, 'com', False, False, False, False, False, True)
    alt_flags(tipoevento, 'ini', False, False, False, False, False, True)
    alt_flags(tipoevento, 'fim', False, False, False, False, False, True)

def false_flags(apps, schema_editor):
    tipoevento = apps.get_model("servico", "TipoEvento")
    for evento in tipoevento.objects.all():
        evento.criar = False
        evento.inativar = False
        evento.ativar = False
        evento.edita_nivel = False
        evento.edita_equipe = False
        evento.edita_descricao = False
        evento.save()


class Migration(migrations.Migration):

    dependencies = [
        ('servico', '0018_tipoevento_flags'),
    ]

    operations = [
        migrations.RunPython(
            init_flags, false_flags),
    ]
