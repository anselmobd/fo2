from pprint import pprint

from base.views import O2BaseGetView

import logistica.models


class EntradaNfLista(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(EntradaNfLista, self).__init__(*args, **kwargs)
        self.template_name = 'logistica/entrada_nf/lista.html'
        self.title_name = 'Lista NF de entrada'

    def mount_context(self):
        dados = logistica.models.NfEntrada.objects.all().values()

        self.context.update({
            'headers': (
                'emissor', 'numero', 'descricao', 'qtd',
                'hora_entrada', 'transportadora', 'motorista', 'placa',
                'responsavel', 'usuario', 'quando'
            ),
            'fields': (
                'emissor', 'numero', 'descricao', 'qtd',
                'hora_entrada', 'transportadora', 'motorista', 'placa',
                'responsavel', 'usuario', 'quando'
            ),
            'dados': dados,
        })




