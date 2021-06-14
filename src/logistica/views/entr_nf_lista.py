from pprint import pprint

from base.views import O2BaseGetView

import logistica.models


class EntradaNfLista(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(EntradaNfLista, self).__init__(*args, **kwargs)
        self.template_name = 'logistica/entrada_nf/lista.html'
        self.title_name = 'Lista NF de entrada'

    def mount_context(self):
        fields = (
            'emissor', 'numero', 'descricao', 'qtd',
            'hora_entrada', 'transportadora', 'motorista', 'placa',
            'responsavel', 'usuario__username', 'quando'
        )
        dados = logistica.models.NfEntrada.objects.all().values(*fields)
        pprint(dados)

        self.context.update({
            'headers': (
                'Emissor', 'NF', 'Descrição', 'Quant.',
                'Hora de entrada', 'Transportadora', 'Motorista', 'Placa',
                'Responsável', 'Digitado por', 'Digitado em'
            ),
            'fields': fields,
            'dados': dados,
        })




