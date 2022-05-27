from pprint import pprint

from fo2.connections import db_cursor_so

from base.views import O2BaseGetView
from utils.functions import untuple_keys_concat

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

        conta_lotes = InventarioLote.objects.count()

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
        data_show = []
        has_row = True
        while has_row:
            lotes = []
            for _ in range(self.quant_inconsist):
                try:
                    row = next(idata)
                    pprint(row)
                    lotes.append(row['lote'])
                except StopIteration:
                    has_row = False
                    break

            qtds_lotes_63 = get_qtd_lotes_63(cursor, lotes)
            qtds_lotes = {
                f"{row['lote']}": row
                for row in qtds_lotes_63
            }

            for row in data:
                if row['lote'] in qtds_lotes:
                    row_63 = qtds_lotes[row['lote']]
                    row['qtd_63'] = row_63['qtd']
                    if row['quantidade'] == row['qtd_63']:
                        continue
                    row['mensagem'] = self.mensagens[
                        compare(
                            row['quantidade'],
                            row['qtd_63'],
                        )
                    ]
                    row['op'] = f"{row_63['op']}"
                    row['periodo'] = f"{row_63['periodo']}"
                    row['oc'] = f"{row_63['oc']}"
                    data_show.append(row)

            if len(data_show) >= self.quant_inconsist:
                break

        data_show = data_show[:self.quant_inconsist]
        fields = {
            'usuario__username': "Usuário",
            'quando': "Quando",
            'lote': "Lote",
            'quantidade': "Quant. inventariada",
            'mensagem': "Mensagem",
            'qtd_63': "Quant. no estágio 63",
            'op': "OP",
            'periodo': "Periodo",
            'oc': "OC",
        }
        self.context.update({
            'headers': fields.values(),
            'fields': fields.keys(),
            'style': untuple_keys_concat({
                (4, 5, 6): 'text-align: center;',
                (7, 8, 9): 'text-align: right;',
            }),
            'data': data_show,
            'conta_lotes': conta_lotes,
            'quant_inconsist': self.quant_inconsist,
        })


def compare(a, b):
    return (a > b) - (a < b) 