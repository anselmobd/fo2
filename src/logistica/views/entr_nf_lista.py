from pprint import pprint

from django.urls import reverse

from base.views import O2BaseGetView
from utils.functions.cadastro import CNPJ

import logistica.models


class EntradaNfLista(O2BaseGetView):
    def __init__(self, *args, **kwargs):
        super(EntradaNfLista, self).__init__(*args, **kwargs)
        self.template_name = "logistica/entrada_nf/lista.html"
        self.title_name = "Lista NF de entrada"

    def mount_context(self):
        fields = (
            "cadastro",
            "numero",
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
        dados = (
            logistica.models.NfEntrada.objects.all().values(*fields).order_by("-quando")
        )

        cnpj = CNPJ()
        for row in dados:
            row["cadastro"] = cnpj.mask(row["cadastro"])
            row["numero|LINK"] = reverse(
                "logistica:entr_nf_historico", args=[row["id"]]
            )

        self.context.update(
            {
                "headers": (
                    "CNPJ",
                    "NF",
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
            }
        )
