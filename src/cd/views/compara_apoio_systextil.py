from operator import itemgetter
from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin

from fo2.connections import db_cursor_so

from base.paginator import paginator_basic
from base.views import O2BaseGetView

import lotes.models

from cd.functions.estante import (
    gera_estantes_enderecos,
    gera_quarto_andar_enderecos,
    gera_lateral_enderecos,
    gera_externos_s_enderecos,
)
from cd.queries.endereco import (
    add_endereco,
    query_endereco,
)
from cd.views.endereco_conteudo_importa import EnderecoImporta


class ComparaApoioSystextil(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(ComparaApoioSystextil, self).__init__(*args, **kwargs)
        self.template_name = 'cd/compara_apoio_systextil.html'
        self.title_name = 'Compara Apoio Systextil'

    def mount_context(self):
        cursor = db_cursor_so(self.request)
        data = query_endereco(cursor, 'IL')

        view_aux = EnderecoImporta()
        ends_importados = set()
        for row in data:
            row['end_antigo'] = view_aux.end_novo_para_antigo(row['end'])
            if row['palete'] != '-':
                ends_importados.add(view_aux.end_novo_para_antigo(row['end']))

        data_rec = lotes.models.Lote.objects
        data_rec = data_rec.filter(local__isnull = False)
        data_apoio = data_rec.values('local')
        ends_faltam = set()
        for row in data_apoio:
            if row['local'] not in ends_importados:
                ends_faltam.add(row['local'])

        # pprint(ends_faltam)

        data = [
            {'end': end}
            for end in ends_faltam
        ]    

        data = sorted(data, key=itemgetter('end'))

        pprint(data)

        # headers = ["Endereço", "Rota", "Palete", "end_antigo"]
        # fields = ['end', 'rota', 'palete', 'end_antigo']
        headers = ["Endereço"]
        fields = ['end']

        self.context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
        })
