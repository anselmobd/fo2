from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView

import produto.forms as forms
import produto.queries as queries


class CustoRef(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(CustoRef, self).__init__(*args, **kwargs)
        self.Form_class = forms.ReferenciaForm
        self.template_name = 'produto/custo_ref.html'
        self.title_name = 'Custo de referência'
        self.get_args = ['ref']

    def mount_context(self):
        ref = self.form.cleaned_data['ref']

        if ref == '':
            return
        self.context.update({
            'ref': ref,
            })

        cursor = db_cursor_so(self.request)

        estruturas = queries.ref_estruturas(cursor, ref)
        if len(estruturas) == 0:
            self.context.update({
                'erro': 'Referência sem estruturas'})
            return
        alternativas = {}
        for estr in estruturas:
            alternativas[estr['ALTERNATIVA']] = estr['DESCR']

        cor_descr = queries.ref_cores(cursor, ref)
        cores = [cd['COR'] for cd in cor_descr]

        tam_descr = queries.ref_tamanhos(cursor, ref)
        tamanhos = [td['TAM'] for td in tam_descr]

        grades = []
        for alt in alternativas.keys():
            alt_data = []
            for cor in cores:
                for tam in tamanhos:
                    data = queries.CustoItem(
                        cursor, '1', ref, tam, cor, alt).get_data()
                    alt_data.append({
                        'COR': cor,
                        'TAM': tam,
                        'CUSTO': data[0]['CUSTO'],
                        'CUSTO|DECIMALS': 3,
                        'DET': '',
                        'DET|TARGET': '_BLANK',
                        'DET|GLYPHICON': 'glyphicon-th-list',
                        'DET|LINK': reverse(
                            'produto:custo__get',
                            args=[1, ref, tam, cor, alt]),
                    })
            grades.append({
                'alt': alt,
                'alt_descr': alternativas[alt],
                'headers': ['Cor', 'Tamanho', 'Custo', 'Detalhe'],
                'fields': ['COR', 'TAM', 'CUSTO', 'DET'],
                'data': alt_data,
            })
        self.context.update({
            'grades': grades,
        })
