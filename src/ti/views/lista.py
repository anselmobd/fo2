from pprint import pprint

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse

from base.views import O2BaseGetPostView

from utils.forms import FiltroForm
import ti.forms
import ti.models


class EquipamentoLista(O2BaseGetPostView):
    def __init__(self, *args, **kwargs):
        super(EquipamentoLista, self).__init__(*args, **kwargs)
        self.template_name = "ti/equipamento_lista.html"
        self.title_name = "Lista equipamentos"
        self.Form_class = ti.forms.EquipamentoListaForm
        self.cleaned_data2self = True
        self.context["por_pagina"] = 50
        self.context["paginas_vizinhas"] = 4

    def mount_context(self):
        fields = (
            "name",
        )

        dados = ti.models.Equipment.objects.all()
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

        self.context.update({
            "headers": (
                "Nome",
            ),
            "fields": fields,
            "dados": dados,
        })
