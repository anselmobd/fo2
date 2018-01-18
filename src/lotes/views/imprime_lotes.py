import errno
from subprocess import Popen, PIPE

from django.shortcuts import render
from django.db import connections
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template import Template, Context
from django.forms.models import model_to_dict

from fo2 import settings
from utils.classes import TermalPrint

from lotes.forms import ImprimeLotesForm, ImprimePacote3LotesForm
import lotes.models as models


class ImprimeLotes(LoginRequiredMixin, View):
    login_url = '/intradm/login/'
    Form_class = ImprimeLotesForm
    template_name = 'lotes/imprime_lotes.html'
    title_name = 'Imprime "Cartela de Lote"'

    def mount_context_and_print(self, cursor, op, tam, cor, order,
                                oc_ininial, oc_final,
                                pula, qtd_lotes, ultimo,
                                impresso, selecao, do_print):
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
        # 'P' = 'Apenas o primeiro de cada 3 lotes semelhantes'
        if selecao == 'P':
            p_cor = ''
            p_tam = ''
        for row in l_data:
            if selecao == 'P':
                if p_cor != row['COR'] or p_tam != row['TAM']:
                    p_cor = row['COR']
                    p_tam = row['TAM']
                    cor_tam_data = models.get_imprime_pocote3lotes(
                        cursor, op, p_tam, p_cor)
                    primeiros_lotes = [r['OC1'] for r in cor_tam_data]
            row['LOTE'] = '{}{:05}'.format(row['PERIODO'], row['OC'])
            if row['OC'] == row['OC1']:
                row['PRIM'] = '*'
            else:
                row['PRIM'] = ''
            if row['DIVISAO'] is None:
                row['DESCRICAO_DIVISAO'] = ''
            if pula_lote:
                pula_lote = row['LOTE'] != ultimo
            else:
                if selecao == 'T' or row['OC'] in primeiros_lotes:
                    data.append(row)

        if len(data) == 0:
            context.update({
                'msg_erro': 'Nehum lote selecionado',
            })
            return context

        # busca informação de OP mãe
        opi_data = models.op_inform(cursor, op)
        opi_row = opi_data[0]
        op_mae = ''
        ref_mae = ''
        if opi_row['TIPO_OP'] == 'Filha de':
            op_mae = opi_row['OP_REL']
            opmaei_data = models.op_inform(cursor, op_mae)
            opmaei_row = opmaei_data[0]
            ref_mae = opmaei_row['REF']
        for row in l_data:
            row['OP_MAE'] = op_mae
            row['REF_MAE'] = ref_mae

        # prepara dados selecionados
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
                        'Estágio', 'Período', 'OC', '1º', 'Quant.', 'Lote',
                        'Unidade', 'OP Mãe', 'Ref. Mãe'),
            'fields': ('OP', 'REF', 'TAM', 'COR',
                       'EST', 'PERIODO', 'OC', 'PRIM', 'QTD', 'LOTE',
                       'DESCRICAO_DIVISAO', 'OP_MAE', 'REF_MAE'),
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
            teg.template(usuario_impresso.modelo.receita, '\r\n')
            teg.printer_start()
            try:
                for row in data:
                    row['op'] = '{}'.format(row['OP'])
                    row['periodo'] = '{}'.format(row['PERIODO'])
                    row['oc'] = '{:05}'.format(row['OC'])
                    row['oc1'] = '{:05}'.format(row['OC1'])
                    row['lote'] = '{}'.format(row['LOTE'])
                    row['ref'] = row['REF']
                    row['tam'] = row['TAM']
                    row['cor'] = row['COR']
                    row['narrativa'] = row['NARRATIVA']
                    row['qtd'] = row['QTD']
                    row['divisao'] = row['DIVISAO']
                    row['descricao_divisao'] = row['DESCRICAO_DIVISAO']
                    if row['DATA_ENTRADA_CORTE']:
                        row['data_entrada_corte'] = \
                            row['DATA_ENTRADA_CORTE'].date()
                    else:
                        row['data_entrada_corte'] = '-'
                    row['estagios'] = estagios
                    row['op_mae'] = row['OP_MAE']
                    row['ref_mae'] = row['REF_MAE']
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
            selecao = form.cleaned_data['selecao']

            cursor = connections['so'].cursor()
            context.update(
                self.mount_context_and_print(
                    cursor, op, tam, cor, order, oc_ininial, oc_final,
                    pula, qtd_lotes, ultimo, impresso, selecao,
                    'print' in request.POST))
        context['form'] = form
        return render(request, self.template_name, context)


class ImprimePacote3Lotes(LoginRequiredMixin, View):
    login_url = '/intradm/login/'
    Form_class = ImprimePacote3LotesForm
    template_name = 'lotes/imprime_pacote3lotes.html'
    title_name = 'Imprime "Pacote de 3 Lotes"'

    def mount_context_and_print(self, cursor, op, tam, cor,
                                pula, qtd_lotes, ultimo, do_print):
        context = {}

        # Pacotes de 3 Lotes
        l_data = models.get_imprime_pocote3lotes(
            cursor, op, tam, cor, pula, qtd_lotes)
        if len(l_data) == 0:
            context.update({
                'msg_erro': 'Nehum lote selecionado',
            })
            return context

        if l_data[0]['SITUACAO'] == 9:
            context.update({
                'msg_erro': 'OP cancelada!',
            })
            l_data = []
            return context

        pula_lote = ultimo != ''
        data = []
        for row in l_data:
            row['LOTE1'] = '{}{:05}'.format(row['PERIODO'], row['OC1'])
            if row['OC2']:
                row['LOTE2'] = '{}{:05}'.format(row['PERIODO'], row['OC2'])
            else:
                row['LOTE2'] = ''
            if row['OC3']:
                row['LOTE3'] = '{}{:05}'.format(row['PERIODO'], row['OC3'])
            else:
                row['LOTE3'] = ''
            if row['PACOTE'] == 1:
                row['PRIM'] = '*'
            else:
                row['PRIM'] = ''
            if pula_lote:
                pula_lote = \
                    row['LOTE1'] != ultimo and \
                    row['LOTE2'] != ultimo and \
                    row['LOTE3'] != ultimo
            else:
                data.append(row)

        if len(data) == 0:
            context.update({
                'msg_erro': 'Nehum lote selecionado',
            })
            return context

        # busca informação de OP mãe
        opi_data = models.op_inform(cursor, op)
        opi_row = opi_data[0]
        op_mae = ''
        ref_mae = ''
        if opi_row['TIPO_OP'] == 'Filha de':
            op_mae = opi_row['OP_REL']
            opmaei_data = models.op_inform(cursor, op_mae)
            opmaei_row = opmaei_data[0]
            ref_mae = opmaei_row['REF']
        for row in l_data:
            row['OP_MAE'] = op_mae
            row['REF_MAE'] = ref_mae

        # prepara dados selecionados
        cod_impresso = 'Cartela de Pacote de 3 Lotes Adesiva'
        context.update({
            'count': len(data),
            'cod_impresso': cod_impresso,
            'headers': ('OP', 'Referência', 'Cor', 'Tamanho', '1º',
                        'Lote 1', 'Lote 2', 'Lote 3', 'OP Mãe', 'Ref. Mãe'),
            'fields': ('OP', 'REF', 'COR', 'TAM', 'PRIM',
                       'LOTE1', 'LOTE2', 'LOTE3', 'OP_MAE', 'REF_MAE'),
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
            teg.template(usuario_impresso.modelo.receita, '\r\n')
            teg.printer_start()
            try:
                for row in data:
                    row['op'] = '{}'.format(row['OP'])
                    row['lote1'] = '{}'.format(row['LOTE1'])
                    row['lote2'] = '{}'.format(row['LOTE2'])
                    row['lote3'] = '{}'.format(row['LOTE3'])
                    row['prim'] = row['PRIM']
                    row['ref'] = row['REF']
                    row['tam'] = row['TAM']
                    row['cor'] = row['COR']
                    row['narrativa'] = row['NARRATIVA']
                    row['estagios'] = estagios
                    row['ref_mae'] = row['REF_MAE']
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
            pula = form.cleaned_data['pula']
            qtd_lotes = form.cleaned_data['qtd_lotes']
            ultimo = form.cleaned_data['ultimo']

            cursor = connections['so'].cursor()
            context.update(
                self.mount_context_and_print(
                    cursor, op, tam, cor, pula, qtd_lotes, ultimo,
                    'print' in request.POST))
        context['form'] = form
        return render(request, self.template_name, context)
