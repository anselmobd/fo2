from pprint import pprint, pformat

from django.db import connections

from base.views import O2BaseGetPostView

import produto.forms as forms
import produto.queries as queries


class Custo(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(Custo, self).__init__(*args, **kwargs)
        self.Form_class = forms.CustoDetalhadoForm
        self.template_name = 'produto/custo.html'
        self.title_name = 'Custo de item'
        self.get_args = ['ref', 'tamanho', 'cor', 'alternativa']

    def mount_context(self):
        ref = self.form.cleaned_data['ref']
        tamanho = self.form.cleaned_data['tamanho']
        cor = self.form.cleaned_data['cor']
        alternativa = self.form.cleaned_data['alternativa']

        if ref == '':
            return
        self.context.update({
            'ref': ref,
            })

        cursor = connections['so'].cursor()

        info = queries.ref_inform(cursor, ref)
        if len(info) == 0:
            self.context.update({'erro': 'Referência não encontrada'})
            return

        alternativas = queries.ref_estruturas(cursor, ref)
        alternativa0 = alternativas[0]
        if cor == '':
            if alternativa0['COR'] == '000000':
                cores = queries.ref_cores(cursor, ref)
                cor = cores[0]['COR']
            else:
                cor = alternativa0['COR']
        else:
            cores = queries.ref_cores(cursor, ref)
            if cor not in [c['COR'] for c in cores]:
                self.context.update({
                    'erro': 'Cor não existe nessa referência'})
                return

        if tamanho == '':
            if alternativa0['TAM'] == '000':
                tamanhos = queries.ref_tamanhos(cursor, ref)
                tam = tamanhos[0]['TAM']
            else:
                tam = alternativa0['TAM']
        else:
            tamanhos = queries.ref_tamanhos(cursor, ref)
            if tamanho in [t['TAM'] for t in tamanhos]:
                tam = tamanho
            else:
                self.context.update({
                    'erro': 'Tamanho não existe nessa referência'})
                return

        if alternativa is None:
            alt = alternativa0['ALTERNATIVA']
            alt_descr = alternativa0['DESCR']
        else:
            if alternativa in [a['ALTERNATIVA'] for a in alternativas]:
                alt = alternativa
                alt_descr = [
                    a['DESCR']
                    for a in alternativas
                    if a['ALTERNATIVA'] == alt][0]
            else:
                self.context.update({
                    'erro': 'Alternativa não existe nessa referência'})
                return

        data = queries.CustoItem(cursor, '1', ref, tam, cor, alt).get_data()

        data[0]['|STYLE'] = 'font-weight: bold;'
        data[0]['CONSUMO'] = ''
        data[0]['PRECO'] = ''

        max_estrut_nivel = 0
        max_digits_consumo = 0
        max_digits_preco = 0
        for row in data:
            max_estrut_nivel = max(max_estrut_nivel, row['ESTRUT_NIVEL'])
            num_digits_consumo = str(row['CONSUMO'])[::-1].find('.')
            max_digits_consumo = max(max_digits_consumo, num_digits_consumo)
            if row['NIVEL'] != '1':
                num_digits_preco = str(row['PRECO'])[::-1].find('.')
                max_digits_preco = max(max_digits_preco, num_digits_preco)
        ident = 1
        for row in data:
            row['CONSUMO|DECIMALS'] = max_digits_consumo
            row['PRECO|DECIMALS'] = max_digits_preco
            row['CUSTO|DECIMALS'] = 3
            if row['ESTRUT_NIVEL'] != 0:
                row['|STYLE'] = 'padding-left: {}em;'.format(
                    row['ESTRUT_NIVEL']*ident)
            padding = (max_estrut_nivel + 1 - row['ESTRUT_NIVEL']) * ident
            for field in ['CONSUMO', 'PRECO', 'CUSTO']:
                row[f'{field}|STYLE'] = f'padding-right: {padding}em;'

        self.context.update({
            'cor': cor,
            'tam': tam,
            'alt': alt,
            'alt_descr': alt_descr,
            'headers': ['Estrutura',
                        'Sequência', 'Nível', 'Referência',
                        'Tamanho', 'Cor', 'Narrativa',
                        'Alternativa', 'Consumo', 'Preço', 'Custo'],
            'fields': ['ESTRUT_NIVEL',
                       'SEQ', 'NIVEL', 'REF',
                       'TAM', 'COR', 'DESCR',
                       'ALT', 'CONSUMO', 'PRECO', 'CUSTO'],
            'style': {9: 'text-align: right;',
                      10: 'text-align: right;',
                      11: 'text-align: right;'},
            'data': data,
        })
