from pprint import pprint

from django.shortcuts import render
from django.views import View

from fo2.connections import db_cursor_so

from utils.functions import untuple_keys_concat
from utils.views import totalize_grouped_data

import insumo.queries

from estoque import forms, queries


class ValorMp(View):
    Form_class = forms.ValorForm
    template_name = 'estoque/valor_mp.html'
    title_name = 'Valor de MP'

    def mount_context(
            self, cursor, nivel, positivos, zerados, negativos, preco_zerado,
            deposito_compras):
        context = {
            'nivel': nivel,
            'positivos': positivos,
            'zerados': zerados,
            'negativos': negativos,
            'preco_zerado': preco_zerado,
            'deposito_compras': deposito_compras,
        }

        data = queries.valor_mp(
            cursor, nivel, positivos, zerados, negativos, preco_zerado,
            deposito_compras)
        if len(data) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context


        data_pedido = insumo.queries.mapa_compras_necessidades_nivel_atual(
            cursor, nivel)

        totalize_grouped_data(data, {
            'group': ['nivel'],
            'sum': ['total'],
            'count': [],
            'descr': {'deposito': 'Total:'}
        })

        for row in data:
            row['qtd|DECIMALS'] = 2
            row['preco|DECIMALS'] = 2
            row['total|DECIMALS'] = 2
            key = (row['ref'], row['tam'], row['cor'])
            try:
                row['pedidos'] = data_pedido[key]
            except Exception:
                row['pedidos'] = 0

        for row in data:
            row['pedidos'] = round(row['pedidos'])

        context.update({
            'headers': ('Nível', 'Referência', 'Descr. Ref.', 'Tamanho', 'Cor',
                        'Conta estoque', 'Depósito', 'Pedidos',
                        'Estoque mínimo', 'Reposição',
                        'Quantidade', 'Preço', 'Total'),
            'fields': ('nivel', 'ref', 'descr_ref', 'tam', 'cor',
                       'conta_estoque', 'deposito', 'pedidos',
                       'estoque_minimo', 'tempo_reposicao',
                       'qtd', 'preco', 'total'),
            'style': untuple_keys_concat({
                (8, 9, 10, 11, 12, 13): 'text-align: right;',
            }),
            'data': data,
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            nivel = form.cleaned_data['nivel']
            positivos = form.cleaned_data['positivos']
            zerados = form.cleaned_data['zerados']
            negativos = form.cleaned_data['negativos']
            preco_zerado = form.cleaned_data['preco_zerado']
            deposito_compras = form.cleaned_data['deposito_compras']
            cursor = db_cursor_so(request)
            context.update(self.mount_context(
                cursor, nivel, positivos, zerados, negativos, preco_zerado,
                deposito_compras))
        context['form'] = form
        return render(request, self.template_name, context)
