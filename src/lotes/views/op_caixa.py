from pprint import pprint

from django.shortcuts import render
from django.views import View

from fo2.connections import db_cursor_so

from utils.views import totalize_grouped_data, group_rowspan

import lotes.functions
import lotes.queries
from lotes.forms import OpForm


class OpCaixa(View):
    Form_class = OpForm
    template_name = 'lotes/op_caixa.html'
    title_name = 'Lista caixas de OP'


    def mount_context(self, cursor, op):
        self.context = {'op': op}

        if not lotes.functions.lotes_em_caixa(self, cursor, op):
            return
        data = self.context['data']

        totalize_grouped_data(data, {
            'group': ['cor'],
            'sum': ['qtd'],
            'count': [],
            'descr': {'op': 'Cor'},
            'global_sum': ['qtd'],
            'global_descr': {'op': 'Total'},
            'empty': '-',
            'clean_pipe': True,
        })
        group = ['op', 'ref', 'num_caixa_txt',
                    'cor', 'tam', 'cor_tam_caixa_txt', 'qtd_caixa']
        group_rowspan(data, group)
        self.context.update({
            'headers': ('OP', 'Referência', 'Cx.OP',
                        'Cor', 'Tamanho', 'Cx.C/T', 'Peças',
                        'Lote', 'Quant.', 'Peso'),
            'fields': ('op', 'ref', 'num_caixa_txt',
                        'cor', 'tam', 'cor_tam_caixa_txt', 'qtd_caixa',
                        'lote', 'qtd', 'peso'),
            'group': group,
            'data': data,
        })

        return

    def get(self, request, *args, **kwargs):
        if 'op' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'op' in kwargs:
            form.data['op'] = kwargs['op']
        if form.is_valid():
            op = form.cleaned_data['op']
            cursor = db_cursor_so(request)
            self.mount_context(cursor, op)
        self.context['form'] = form
        return render(request, self.template_name, self.context)
