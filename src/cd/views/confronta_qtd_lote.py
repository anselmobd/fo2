from pprint import pprint

from fo2.connections import db_cursor_so

from base.views import O2BaseGetView
from utils.functions import untuple_keys_concat

from lotes.models.inventario import (
    Inventario,
    InventarioLote,
)


from cd.queries.inventario_lote import get_qtd_lotes_63


class ConfrontaQtdLote(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(ConfrontaQtdLote, self).__init__(*args, **kwargs)
        self.template_name = 'cd/confronta_qtd_lote.html'
        self.title_name = 'Confronta quant. lotes'
        self.quant_inconsist = 100
        self.mensagens = {
            -1: "menor que",
            0: "igual a",
            1: "maior que",
        }

    def calcula_diferencas(self):
        for row in InventarioLote.objects.filter(diferenca=None):
            qtds_lotes_63 = get_qtd_lotes_63(self.cursor, row.lote)
            if qtds_lotes_63:
                row.diferenca = row.quantidade - qtds_lotes_63[0]['qtd']
                row.save()

    def zera_diferenca(self, lote, quando):
        row_lote = InventarioLote.objects.get(lote=lote, quando=quando)
        row_lote.diferenca = 0
        row_lote.save()

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        self.calcula_diferencas()

        lotes = InventarioLote.objects.filter(
            inventario=Inventario.objects.order_by('inicio').last()
        )
        conta_lotes = lotes.count()
        conta_corretos = lotes.filter(diferenca=0).count()

        invent_lote = lotes.exclude(diferenca=None)
        invent_lote = invent_lote.order_by(
            'quando',
        ).values(
            'lote',
            'quantidade',
            'usuario__username',
            'quando',
        )
        iter_invent_lote = iter(invent_lote)
        data_show = []
        has_row = True
        while has_row:
            lotes_parcial = []
            invent_parcial = []
            for _ in range(self.quant_inconsist):
                try:
                    row = next(iter_invent_lote)
                    pprint(row)
                    lotes_parcial.append(row['lote'])
                    invent_parcial.append(row)
                except StopIteration:
                    has_row = False
                    break

            lotes_63 = get_qtd_lotes_63(self.cursor, lotes_parcial)
            lotes_63_dict = {
                f"{row['lote']}": row
                for row in lotes_63
            }

            for row in invent_parcial:
                if row['lote'] in lotes_63_dict:
                    row_63 = lotes_63_dict[row['lote']]
                    row['qtd_63'] = row_63['qtd']
                    if row['quantidade'] == row['qtd_63']:
                        self.zera_diferenca(row['lote'], row['quando'])
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
            'conta_corretos': conta_corretos,
            'conta_inconsistentes': conta_lotes - conta_corretos,
            'quant_inconsist': self.quant_inconsist,
        })


def compare(a, b):
    return (a > b) - (a < b) 