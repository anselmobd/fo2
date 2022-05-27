from pprint import pprint

from fo2.connections import db_cursor_so

from base.views import O2BaseGetView

from lotes.models.inventario import InventarioLote
from cd.queries.inventario_lote import get_qtd_lotes_63


class ConfrontaQtdLote(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(ConfrontaQtdLote, self).__init__(*args, **kwargs)
        self.template_name = 'cd/confronta_qtd_lote.html'
        self.title_name = 'Confronta quant. lotes'
        self.quant_inconsist = 20
        self.mensagens = {
            -1: "é menor que",
            0: "é igual a",
            1: "é maior que",
        }

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        data = InventarioLote.objects.all()
        data = data.order_by(
            'quando',
        ).values(
            'lote',
            'quantidade',
            'usuario__username',
            'quando',
        )
        idata = iter(data)
        lotes = []
        data_show = []
        todos = False
        while True:
            for _ in range(self.quant_inconsist):
                try:
                    row = next(idata)
                    pprint(row)
                    lotes.append(row['lote'])
                except StopIteration:
                    todos = True
                    break

            qtds_lotes_63 = get_qtd_lotes_63(cursor, lotes)
            qtds_lotes = {
                f"{row['lote']}": row['qtd']
                for row in qtds_lotes_63
            }

            for row in data:
                if row['lote'] in qtds_lotes:
                    row['qtd_63'] = qtds_lotes[row['lote']]
                    if row['quantidade'] == row['qtd_63']:
                        continue
                    row['mensagem'] = self.mensagens[
                        compare(
                            row['quantidade'],
                            row['qtd_63'],
                        )
                    ]
                    data_show.append(row)

            if len(data_show) >= self.quant_inconsist or todos:
                break

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
            'data': data_show,
            'quant_inconsist': self.quant_inconsist,
        })


def compare(a, b):
    return (a > b) - (a < b) 