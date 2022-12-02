from pprint import pprint

from fo2.connections import db_cursor_so

from o2.views.base.get_post import O2BaseGetPostView
from utils.functions import untuple_keys_concat
from utils.functions.logica import compare

from lotes.models.inventario import (
    Inventario,
    InventarioLote,
)

from cd.forms import ConfrontaQtdLoteForm
from cd.queries.inventario_lote import get_qtd_lotes_63


class ConfrontaQtdLote(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(ConfrontaQtdLote, self).__init__(*args, **kwargs)
        self.Form_class = ConfrontaQtdLoteForm
        self.cleaned_data2self = True
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

    def get_lotes(self):
        lotes = InventarioLote.objects.filter(
            inventario=Inventario.objects.order_by('inicio').last()
        )
        if self.usuario:
            lotes = lotes.filter(
                usuario__username=self.usuario,
            )
        return lotes

    def mount_context(self):
        up = self.kwargs.get('up', False)
 
        self.cursor = db_cursor_so(self.request)

        self.calcula_diferencas()

        lotes = self.get_lotes()

        invent_lote = lotes.exclude(diferenca=0)
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
                    if up and row['quantidade'] <= row_63['qtd_lote']:
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
                    row['qtd_ori'] = f"{row_63['qtd_ori']}"
                    row['qtd_lote'] = f"{row_63['qtd_lote']}"
                    row['ref'] = f"{row_63['ref']}"
                    row['cor'] = f"{row_63['cor']}"
                    row['tam'] = f"{row_63['tam']}"
                    data_show.append(row)

            if len(data_show) >= self.quant_inconsist:
                break

        data_show = data_show[:self.quant_inconsist]

        lotes = self.get_lotes()
        conta_lotes = lotes.count()
        conta_corretos = lotes.filter(diferenca=0).count()

        fields = {
            'usuario__username': "Usuário",
            'quando': "Quando",
            'lote': "Lote",
            'quantidade': "Quant. inventariada",
            'mensagem': "Mensagem",
            'qtd_63': "Quant. estágio 63",
            'qtd_ori': "Tamanho do lote",
            'qtd_lote': "Quant. do lote",
            'op': "OP",
            'periodo': "Periodo",
            'oc': "OC",
            'ref': "Ref.",
            'cor': "Cor",
            'tam': "Tam.",
        }
        self.context.update({
            'headers': fields.values(),
            'fields': fields.keys(),
            'style': untuple_keys_concat({
                (4, 5, 6, 7, 8): 'text-align: center;',
                (9, 10, 11): 'text-align: right;',
            }),
            'data': data_show,
            'conta_lotes': conta_lotes,
            'conta_corretos': conta_corretos,
            'conta_inconsistentes': conta_lotes - conta_corretos,
            'quant_inconsist': self.quant_inconsist,
        })
