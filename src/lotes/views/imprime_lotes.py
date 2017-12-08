import errno
from subprocess import Popen, PIPE
from pprint import pprint

from django.shortcuts import render
from django.db import connections
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template import Template, Context
from django.forms.models import model_to_dict

from fo2 import settings
from utils.classes import TermalPrint

from lotes.forms import ImprimeLotesForm
import lotes.models as models


class ImprimeLotes(LoginRequiredMixin, View):
    login_url = '/intradm/login/'
    Form_class = ImprimeLotesForm
    template_name = 'lotes/imprime_lotes.html'
    title_name = 'Imprime "Cartela de Lote"'

    def mount_context_and_print(self, cursor, op, tam, cor, order,
                                oc_ininial, oc_final,
                                pula, qtd_lotes, ultimo,
                                impresso, do_print):
        context = {}

        oc_ininial_val = oc_ininial or 0
        oc_final_val = oc_final or 99999

        # Lotes ordenados por OC
        l_data = models.get_imprime_lotes(
            cursor, op, tam, cor, order, oc_ininial_val, oc_final_val,
            pula, qtd_lotes)
        if len(l_data) == 0:
            context.update({
                'msg_erro': 'Nehum lote selecionado',
            })
            return context

        if l_data[0]['OP_SITUACAO'] == 9:
            context.update({
                'msg_erro': 'OP cancelada!',
            })
            l_data = []
            return context
        pula_lote = ultimo != ''
        data = []
        for row in l_data:
            row['LOTE'] = '{}{:05}'.format(row['PERIODO'], row['OC'])
            if row['DIVISAO'] is None:
                row['DESCRICAO_DIVISAO'] = ''
            if pula_lote:
                pula_lote = row['LOTE'] != ultimo
            else:
                data.append(row)

        if len(data) == 0:
            context.update({
                'msg_erro': 'Nehum lote selecionado',
            })
            return context

        if impresso == 'A':
            cod_impresso = 'Cartela de Lote Adesiva'
        elif impresso == 'C':
            cod_impresso = 'Cartela de Lote Cartão'
        else:
            cod_impresso = 'Cartela de Fundo'
        context.update({
            'count': len(data),
            'cod_impresso': cod_impresso,
            'headers': ('OP', 'Referência', 'Tamanho', 'Cor',
                        'Estágio', 'Período', 'OC', 'Quant.', 'Lote',
                        'Unidade'),
            'fields': ('OP', 'REF', 'TAM', 'COR',
                       'EST', 'PERIODO', 'OC', 'QTD', 'LOTE',
                       'DESCRICAO_DIVISAO'),
            'data': data,
        })

        if do_print:
            try:
                impresso = models.Impresso.objects.get(
                    nome=cod_impresso)
            except models.Impresso.DoesNotExist:
                impresso = None
            if impresso is None:
                context.update({
                    'msg_erro': 'Impresso não cadastrado',
                })
                do_print = False

        if do_print:
            try:
                usuario_impresso = models.UsuarioImpresso.objects.get(
                    usuario=self.request.user, impresso=impresso)
            except models.UsuarioImpresso.DoesNotExist:
                usuario_impresso = None
            if usuario_impresso is None:
                context.update({
                    'msg_erro': 'Impresso não cadastrado para o usuário',
                })
                do_print = False

        if do_print:
            e_data = models.op_estagios(cursor, op)
            estagios = []
            for e_row in e_data:
                estagios.append(e_row['EST'])
            teg = TermalPrint(usuario_impresso.impressora_termica.nome)
            teg.template(usuario_impresso.modelo.modelo, '\r\n')
            teg.printer_start()
            try:
                for row in data:
                    row['op'] = '{:09}'.format(row['OP'])
                    row['periodo'] = '{}'.format(row['PERIODO'])
                    row['oc'] = '{:05}'.format(row['OC'])
                    row['lote'] = '{}'.format(row['LOTE'])
                    row['ref'] = row['REF']
                    row['tam'] = row['TAM']
                    row['cor'] = row['COR']
                    row['narrativa'] = row['NARRATIVA']
                    row['qtd'] = row['QTD']
                    row['divisao'] = row['DIVISAO']
                    row['descricao_divisao'] = row['DESCRICAO_DIVISAO']
                    row['data_entrada_corte'] = \
                        row['DATA_ENTRADA_CORTE'].date()
                    row['estagios'] = estagios
                    pprint(estagios)
                    teg.context(row)
                    teg.printer_send()
            finally:
                teg.printer_end()

        return context

    def get(self, request):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.request = request
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            op = form.cleaned_data['op']
            tam = form.cleaned_data['tam']
            cor = form.cleaned_data['cor']
            order = form.cleaned_data['order']
            oc_ininial = form.cleaned_data['oc_ininial']
            oc_final = form.cleaned_data['oc_final']
            pula = form.cleaned_data['pula']
            qtd_lotes = form.cleaned_data['qtd_lotes']
            ultimo = form.cleaned_data['ultimo']
            impresso = form.cleaned_data['impresso']

            cursor = connections['so'].cursor()
            context.update(
                self.mount_context_and_print(
                    cursor, op, tam, cor, order, oc_ininial, oc_final,
                    pula, qtd_lotes, ultimo, impresso, 'print' in request.POST))
        context['form'] = form
        return render(request, self.template_name, context)
