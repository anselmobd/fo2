from pprint import pprint

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse

from o2.views.base.get_post import O2BaseGetPostView
from utils.functions.cadastro import CNPJ

import logistica.forms
import logistica.models


class EntradaNfLista(O2BaseGetPostView):
    def __init__(self, *args, **kwargs):
        super(EntradaNfLista, self).__init__(*args, **kwargs)
        self.template_name = "logistica/entrada_nf/lista.html"
        self.title_name = "Lista NF de entrada"
        self.Form_class = logistica.forms.ListaForm
        self.cleaned_data2self = True
        self.context["por_pagina"] = 50
        self.context["paginas_vizinhas"] = 4

    def mount_context(self):
        tipo_nota = dict(logistica.models.NfEntrada.TIPO_NOTA)
        fields = (
            "cadastro",
            "numero",
            "tipo",
            "emissor",
            "descricao",
            "volumes",
            "chegada",
            "transportadora",
            "motorista",
            "placa",
            "responsavel",
            "usuario__username",
            "quando",
            "id",
        )

        dados = logistica.models.NfEntrada.objects.all()
        if self.numero:
            dados = dados.filter(numero=self.numero)
        if self.data:
            dados = dados.filter(chegada__contains=self.data)
        dados = dados.values(*fields).order_by("-quando")

        paginator = Paginator(dados, self.context["por_pagina"])
        try:
            dados = paginator.page(self.pagina)
        except PageNotAnInteger:
            dados = paginator.page(1)
        except EmptyPage:
            dados = paginator.page(paginator.num_pages)

        cnpj = CNPJ()
        for row in dados:
            row["cadastro"] = cnpj.mask(row["cadastro"])
            row["numero|LINK"] = reverse(
                "logistica:entr_nf_historico", args=[row["id"]]
            )
            row["tipo"] = tipo_nota[row["tipo"]]

        self.context.update({
            "headers": (
                "CNPJ",
                "NF",
                "Tipo",
                "Emissor",
                "Descrição",
                "Volumes",
                "Chegada",
                "Transportadora",
                "Motorista",
                "Placa",
                "Responsável",
                "Digitado por",
                "Digitado em",
            ),
            "fields": fields[:-1],
            "dados": dados,
        })
