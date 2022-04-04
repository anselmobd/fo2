from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.classes import TermalPrint

import lotes.models

from cd.forms.endereco import EnderecoImprimeForm
from cd.queries.endereco import (
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

    def importa(self):
        lotes_s = lotes_em_endereco(self.cursor, self.inicial)
        print(self.inicial)
        pprint(lotes_s)

        end_antigo = self.end_novo_para_antigo(
            self.inicial)
        lotes_a = self.lotes_end_apoio(end_antigo)
        print(end_antigo)
        pprint(lotes_a)

        self.context.update({
            'mensagem': f'{len(lotes_s)} lotes',
        })
        return False

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        self.inicial = self.inicial.upper()
        self.final = self.final.upper()

        self.data = query_endereco(self.cursor, 'TO')

        if not next(
            (
                row for row in self.data
                if row["end"] == self.inicial
            ),
            False
        ):
            self.context.update({
                'mensagem': 'Endereço inicial não existe',
            })
            return

        if not next(
            (
                row for row in self.data
                if row["end"] == self.final
            ),
            False
        ):
            self.context.update({
                'mensagem': 'Endereço final não existe',
            })
            return

        if self.importa():
            self.context.update({
                'mensagem': 'OK!',
            })
