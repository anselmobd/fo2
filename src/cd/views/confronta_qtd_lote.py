from pprint import pprint

from fo2.connections import db_cursor_so

from base.paginator import paginator_basic
from base.views import O2BaseGetView

from lotes.models.inventario import InventarioLote
from cd.queries.inventario_lote import get_qtd_lotes_63


class ConfrontaQtdLote(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(ConfrontaQtdLote, self).__init__(*args, **kwargs)
        self.template_name = 'cd/confronta_qtd_lote.html'
        self.title_name = 'Confronta quant. lotes'
        self.por_pagina = 20

    def mount_context(self):
        cursor = db_cursor_so(self.request)
        page = self.request.GET.get('page', 1)

        data = InventarioLote.objects.all()
        data = data.order_by(
            'quando',
        ).values(
            'lote',
            'quantidade',
            'usuario__username',
            'quando',
        )
        qtd_invent = len(data)

        data = paginator_basic(data, self.por_pagina, page)

        lotes = [
            row['lote']
            for row in data
        ]
        qtds_lotes_63 = get_qtd_lotes_63(cursor, lotes)
        qtds_lotes = {
            f"{row['lote']}": row['qtd']
            for row in qtds_lotes_63
        }

        mensagens = {
            -1: "é menor que",
            0: "é igual a",
            1: "é maior que",
        }

        for row in data:
            row['qtd_63'] = qtds_lotes[row['lote']]
            row['mensagem'] = mensagens[
                compare(
                    row['quantidade'],
                    row['qtd_63'],
                )
            ]

        fields = {
            'lote': "Lote",
            'quantidade': "Quantidade inventariada",
            'mensagem': "Mensagem",
            'qtd_63': "Quantidade no estágio 63",
            'usuario__username': "Usuário",
            'quando': "Quando",
        }
        self.context.update({
            'headers': fields.values(),
            'fields': fields.keys(),
            'data': data,
            'qtd_invent': qtd_invent,
            'por_pagina': self.por_pagina,
        })


def compare(a, b):
    return (a > b) - (a < b) 