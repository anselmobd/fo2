from pprint import pprint, pformat
from collections import OrderedDict

from django.contrib.auth.mixins import PermissionRequiredMixin

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.classes import TermalPrint

import lotes.models

from cd.forms.endereco import EnderecoImprimeForm
from cd.queries.endereco import (
    add_lote_in_endereco,
    lotes_em_endereco, 
    query_endereco,
)


class EnderecoImporta(PermissionRequiredMixin, O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(EnderecoImporta, self).__init__(*args, **kwargs)
        self.Form_class = EnderecoImprimeForm
        self.form_class_has_initial = True
        self.cleaned_data2self = True
        self.permission_required = 'cd.can_admin_pallet'
        self.template_name = 'cd/endereco_conteudo_importa.html'
        self.title_name = 'Importa conteudo de endereços'
        self.cleaned_data2self = True

    def end_novo_para_antigo(self, endereco):
        if endereco[1] in 'ABCDEFGH':
            return endereco[1]+endereco[3:]

    def lotes_end_apoio(self, endereco):
        data_rec = lotes.models.Lote.objects
        data_rec = data_rec.filter(local=endereco)
        data_rec = data_rec.order_by('op', 'lote')
        data = data_rec.values('op', 'lote')
        return list(data)

    def row_exist(self, row_a):
        for row_s in self.lotes_s:
            if (
                row_s['op'] == row_a['op'] and
                row_s['lote'] == row_a['lote']
            ):
                return True
        return False

    def importa_end(self, endereco):
        self.lotes_s = lotes_em_endereco(self.cursor, endereco)
        palete = self.lotes_s[0]['palete']
        print(endereco)
        pprint(self.lotes_s)

        if not palete:
            return {endereco: 'sem palete'}

        end_antigo = self.end_novo_para_antigo(
            endereco)
        lotes_a = self.lotes_end_apoio(end_antigo)
        print(end_antigo)
        pprint(lotes_a)

        result = {}
        for row_a in lotes_a:
            if not self.row_exist(row_a):
                print('inclui em', palete)
                pprint(row_a)
                if add_lote_in_endereco(
                    self.cursor,
                    palete,
                    row_a['op'],
                    row_a['lote'],
                ):
                    key = 'OK'
                else:
                    key = 'ERRO'
                try:
                    result[key].append(row_a['lote'])
                except Exception:
                    result[key] = [row_a['lote']]
                # break
                
        return {endereco: result}

    def importa(self):
        result = OrderedDict()
        for row in self.data[self.primeiro:self.ultimo+1]:
            result.update(
                self.importa_end(row['end'])
            )
        self.context.update({
            'mensagem': 'Processado',
            'log': pformat(result),
        })

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        self.inicial = self.inicial.upper()
        self.final = self.final.upper()

        self.data = query_endereco(self.cursor, 'TO')

        self.primeiro = next(
            (
                idx for idx, row in enumerate(self.data)
                if row["end"] == self.inicial
            )
        )
        pprint(self.primeiro)
        if not self.primeiro:
            self.context.update({
                'mensagem': 'Endereço inicial não existe',
            })
            return

        self.ultimo = next(
            (
                idx for idx, row in enumerate(self.data)
                if row["end"] == self.final
            )
        )
        pprint(self.ultimo)
        if not self.ultimo:
            self.context.update({
                'mensagem': 'Endereço final não existe',
            })
            return

        if self.ultimo < self.primeiro:
            self.context.update({
                'mensagem': 'Endereço final anterior ao inicial',
            })
            return

        self.importa()
