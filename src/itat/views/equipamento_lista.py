from pprint import pprint

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse

from base.views import O2BaseGetPostView

import itat.forms
import itat.models


class EquipamentoLista(O2BaseGetPostView):
    def __init__(self, *args, **kwargs):
        super(EquipamentoLista, self).__init__(*args, **kwargs)
        self.template_name = "itat/equipamento_lista.html"
        self.title_name = "Lista equipamentos"
        self.Form_class = itat.forms.EquipamentoListaForm
        self.cleaned_data2self = True
        self.context["por_pagina"] = 50
        self.context["paginas_vizinhas"] = 4

    def mount_context(self):
        fields = (
            "type__name",
            "name",
            "description",
            "application",
            "users",
            "primary_ip",
        )

        dados = itat.models.Equipment.objects.all()
        if self.filtro:
            dados = dados.filter(name__icontains=self.filtro)
        dados = dados.values(*fields).order_by("name")

        paginator = Paginator(dados, self.context["por_pagina"])
        try:
            dados = paginator.page(self.pagina)
        except PageNotAnInteger:
            dados = paginator.page(1)
        except EmptyPage:
            dados = paginator.page(paginator.num_pages)

        for row in dados:
            for field in fields:
                if row[field] is None:
                    row[field] = "-"

        self.context.update({
            "headers": (
                "Tipo",
                "Nome",
                "Descrição",
                "Uso",
                "Usuários",
                "IP principal",
            ),
            "fields": fields,
            "dados": dados,
        })
