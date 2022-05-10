# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def set_popassunto_grupoassunto(apps, schema_editor):
    PopAssunto = apps.get_model("geral", "PopAssunto")
    PopGrupoAssunto = apps.get_model("geral", "PopGrupoAssunto")
    for obj in PopAssunto.objects.all():
        obj.grupo_assunto = PopGrupoAssunto.objects.get(slug=obj.grupo_slug)
        obj.save()


def unset_popassunto_grupoassunto(apps, schema_editor):
    PopAssunto = apps.get_model("geral", "PopAssunto")
    PopGrupoAssunto = apps.get_model("geral", "PopGrupoAssunto")
    for obj in PopAssunto.objects.all():
        obj.grupo_assunto = PopGrupoAssunto.objects.get(id=1)
        obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('geral', '0043_popassunto_grupo_assunto'),
    ]

    operations = [
        migrations.RunPython(
            set_popassunto_grupoassunto, unset_popassunto_grupoassunto),
    ]
