from pprint import pprint

from base.views import O2BaseGetView
from utils.functions.cadastro import CNPJ

import logistica.models


class EntradaNfLista(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(EntradaNfLista, self).__init__(*args, **kwargs)
        self.template_name = 'logistica/entrada_nf/lista.html'
        self.title_name = 'Lista NF de entrada'

    def mount_context(self):
        fields = (
            'cadastro', 'emissor', 'numero', 'descricao', 'qtd',
            'hora_entrada', 'transportadora', 'motorista', 'placa',
            'responsavel', 'usuario__username', 'quando'
        )
        dados = logistica.models.NfEntrada.objects.all().values(*fields)

        cnpj = CNPJ()
        for row in dados:
            row['cadastro'] = cnpj.mask(row['cadastro'])

        self.context.update({
            'headers': (
                'CNPJ', 'Emissor', 'NF', 'Descrição', 'Quant.',
                'Hora de entrada', 'Transportadora', 'Motorista', 'Placa',
                'Responsável', 'Digitado por', 'Digitado em'
            ),
            'fields': fields,
            'dados': dados,
        })




