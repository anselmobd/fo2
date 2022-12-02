from pprint import pprint

from o2.views.base.get import O2BaseGetView
from utils.functions.cadastro import CNPJ

import logistica.models


class EntradaNfHistorico(O2BaseGetView):
    def __init__(self, *args, **kwargs):
        super(EntradaNfHistorico, self).__init__(*args, **kwargs)
        self.template_name = "logistica/entrada_nf/historico.html"
        self.title_name = "Histórico de NF de entrada"
        self.get_args = ["id"]

    def mount_context(self):
        self.id = self.get_arg("id")
        fields = (
            "cadastro",
            "emissor",
            "numero",
            "descricao",
            "volumes",
            "chegada",
            "transportadora",
            "motorista",
            "placa",
            "responsavel",
            "usuario__username",
            "quando",
        )
        dados = logistica.models.NfEntrada.objects.filter(id=self.id).values(*fields)

        cnpj = CNPJ()
        for row in dados:
            row["cadastro"] = cnpj.mask(row["cadastro"])

        self.context.update(
            {
                "headers": (
                    "CNPJ",
                    "Emissor",
                    "NF",
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
                "fields": fields,
                "dados": dados,
            }
        )
