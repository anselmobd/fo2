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
                                oc_inicial, oc_final,
                                pula, qtd_lotes, ultimo,
                                impresso, order_descr, obs1, obs2, do_print):
        context = {}

        oc_inicial_val = oc_inicial or 0
        oc_final_val = oc_final or 99999

        # Lotes ordenados por OC
        l_data = models.get_imprime_lotes(
            cursor, op, tam, cor, order, oc_inicial_val, oc_final_val,
            pula, qtd_lotes)
        if len(l_data) == 0:
            context.update({
                'msg_erro': 'Nehum lote selecionado',
            })
            return context

        if l_data[0]['op_situacao'] == 9:
            context.update({
                'msg_erro': 'OP cancelada!',
            })
            l_data = []
            return context

        pula_lote = ultimo != ''
        data = []
        for row in l_data:
            row['lote'] = '{}{:05}'.format(row['periodo'], row['oc'])
            if row['oc'] == row['oc1']:
                row['prim'] = '*'
            else:
                row['prim'] = ''
            if row['divisao'] is None:
                row['descricao_divisao'] = ''
            if pula_lote:
                pula_lote = row['lote'] != ultimo
            else:
                data.append(row)

        if len(data) == 0:
            context.update({
                'msg_erro': 'Nehum lote selecionado',
            })
            return context

        ref = l_data[0]['ref']

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
            row['op_mae'] = op_mae
            row['ref_mae'] = ref_mae

        # prepara dados selecionados
        if impresso == 'A':
            cod_impresso = 'Cartela de Lote Adesiva'
        elif impresso == 'C':
            cod_impresso = 'Cartela de Lote Cartão'
        elif impresso == 'F':
            cod_impresso = 'Cartela de Fundo'
        elif impresso == 'E':
            cod_impresso = 'Etiqueta de caixa de lotes'
        context.update({
            'count': len(data),
            'cod_impresso': cod_impresso,
            'ordem': order_descr,
            'op': op,
            'ref': ref,
            'op_mae': op_mae,
            'ref_mae': ref_mae,
            'cor': cor,
            'tam': tam,
            'ultimo': ultimo,
            'pula': pula,
            'qtd_lotes': qtd_lotes,
            'oc_inicial': oc_inicial,
            'oc_final': oc_final,
            'headers': ('Tamanho', 'Cor', 'Período', 'OC', '1º', 'Quant.',
                        'Lote', 'Estágio', 'Unidade'),
            'fields': ('tam', 'cor', 'periodo', 'oc', 'prim', 'qtd',
                       'lote', 'est', 'descricao_divisao'),
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
            teg.template(usuario_impresso.modelo.gabarito, '\r\n')
            teg.printer_start()
            try:
                for row in data:
                    row['obs1'] = obs1
                    row['obs2'] = obs2
                    row['op'] = '{}'.format(row['op'])
                    row['periodo'] = '{}'.format(row['periodo'])
                    row['oc'] = '{:05}'.format(row['oc'])
                    row['oc1'] = '{:05}'.format(row['oc1'])
                    row['lote'] = '{}'.format(row['lote'])
                    if row['data_entrada_corte']:
                        row['data_entrada_corte'] = \
                            row['data_entrada_corte'].date()
                    else:
                        row['data_entrada_corte'] = '-'
                    row['estagios'] = estagios
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
            order_descr = [ord[1] for ord in form.fields['order'].choices
                           if ord[0] == order][0]
            oc_inicial = form.cleaned_data['oc_inicial']
            oc_final = form.cleaned_data['oc_final']
            pula = form.cleaned_data['pula']
            qtd_lotes = form.cleaned_data['qtd_lotes']
            ultimo = form.cleaned_data['ultimo']
            impresso = form.cleaned_data['impresso']
            obs1 = form.cleaned_data['obs1']
            obs2 = form.cleaned_data['obs2']

            cursor = connections['so'].cursor()
            context.update(
                self.mount_context_and_print(
                    cursor, op, tam, cor, order, oc_inicial, oc_final,
                    pula, qtd_lotes, ultimo, impresso, order_descr, obs1, obs2,
                    'print' in request.POST))
        context['form'] = form
        return render(request, self.template_name, context)


class ImprimePacote3Lotes(LoginRequiredMixin, View):
    login_url = '/intradm/login/'
    Form_class = ImprimePacote3LotesForm
    template_name = 'lotes/imprime_pacote3lotes.html'
    title_name = 'Imprime "Pacote de 3 Lotes"'

    def mount_context_and_print(self, cursor, op, tam, cor,
                                parm_pula, parm_qtd_lotes,
                                ultimo, ultima_cx, impresso, impresso_descr,
                                obs1, obs2, do_print):
        context = {}

        # Pacotes de 3 Lotes
        l_data = models.get_imprime_caixas_op_3lotes(cursor, op)

        if len(l_data) == 0:
            context.update({
                'msg_erro': 'Nehum lote selecionado',
            })
            return context

        if l_data[0]['situacao'] == 9:
            context.update({
                'msg_erro': 'OP cancelada!',
            })
            l_data = []
            return context

        ref = l_data[0]['ref']

        # atribui qtd_cortam
        p_cor = ''
        p_tam = ''
        for row in reversed(l_data):
            if p_cor != row['cor'] or p_tam != row['tam']:
                p_cor = row['cor']
                p_tam = row['tam']
                qtd_cortam = row['pacote']
            row['qtd_cortam'] = '{}'.format(qtd_cortam)
            row['cont_cortam'] = '{}'.format(row['pacote'])
            row['cx_ct'] = '{} / {}'.format(row['pacote'], qtd_cortam)

        # completa informações da pesquisa
        qtd_total = len(l_data)
        cont_total = 0
        for row in l_data:
            row['qtd_total'] = '{}'.format(qtd_total)
            cont_total += 1
            row['cont_total'] = '{}'.format(cont_total)
            row['cx_op'] = '{} / {}'.format(cont_total, qtd_total)

            row['lote1'] = '{}{:05}'.format(row['periodo'], row['oc1'])
            row['qtd_lotes'] = '1'
            if row['oc2']:
                row['lote2'] = '{}{:05}'.format(row['periodo'], row['oc2'])
                row['qtd_lotes'] = '2'
            else:
                row['lote2'] = ' '
                row['oc2'] = ''
                row['qtd2'] = ''
            if row['oc3']:
                row['lote3'] = '{}{:05}'.format(row['periodo'], row['oc3'])
                row['qtd_lotes'] = '3'
            else:
                row['lote3'] = ' '
                row['oc3'] = ''
                row['qtd3'] = ''

            if row['pacote'] == 1:
                row['prim'] = '*'
            else:
                row['prim'] = ''

        # filtra resultado
        if parm_pula is None:
            pula = 0
        else:
            pula = parm_pula
        if parm_qtd_lotes is None:
            qtd_lotes = 1000000
        else:
            qtd_lotes = parm_qtd_lotes

        pula_lote = ultimo != '' or ultima_cx != ''
        data = []
        for row in l_data:
            if pula_lote:
                pula_lote = \
                    row['lote1'] != ultimo and \
                    row['lote2'] != ultimo and \
                    row['lote3'] != ultimo and \
                    row['cont_total'] != ultima_cx
            else:
                print_lote = (tam == '' or row['tam'] == tam) \
                    and (cor == '' or row['cor'] == cor)
                if print_lote:
                    if pula > 0:
                        pula -= 1
                    else:
                        if qtd_lotes > 0:
                            data.append(row)
                            qtd_lotes -= 1

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
            op_mae = '{}'.format(opi_row['OP_REL'])
            opmaei_data = models.op_inform(cursor, op_mae)
            opmaei_row = opmaei_data[0]
            ref_mae = opmaei_row['REF']
        for row in l_data:
            row['op_mae'] = op_mae
            row['ref_mae'] = ref_mae

        # prepara dados selecionados
        cod_impresso = impresso_descr
        context.update({
            'count': len(data),
            'cod_impresso': cod_impresso,
            'op': op,
            'ref': ref,
            'op_mae': op_mae,
            'ref_mae': ref_mae,
            'cor': cor,
            'tam': tam,
            'ultima_cx': ultima_cx,
            'ultimo': ultimo,
            'pula': parm_pula,
            'qtd_lotes': parm_qtd_lotes,
            'headers': ('CX.OP', 'Cor', 'Tamanho', '1º', 'CX.Cor/Tam',
                        'Lote 1', 'Qtd. 1', 'Lote 2', 'Qtd. 2',
                        'Lote 3', 'Qtd. 3'),
            'fields': ('cx_op', 'cor', 'tam', 'prim', 'cx_ct',
                       'lote1', 'qtd1', 'lote2', 'qtd2',
                       'lote3', 'qtd3'),
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
            teg.template(usuario_impresso.modelo.gabarito, '\r\n')
            teg.printer_start()
            try:
                for row in data:
                    row['obs1'] = obs1
                    row['obs2'] = obs2
                    row['op'] = '{}'.format(row['op'])
                    row['estagios'] = estagios
                    if row['data_entrada_corte']:
                        row['data_entrada_corte'] = \
                            row['data_entrada_corte'].date()
                    else:
                        row['data_entrada_corte'] = '-'
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
            ultima_cx = form.cleaned_data['ultima_cx']
            impresso = form.cleaned_data['impresso']
            impresso_descr = [ord[1] for ord in form.fields['impresso'].choices
                              if ord[0] == impresso][0]
            obs1 = form.cleaned_data['obs1']
            obs2 = form.cleaned_data['obs2']

            cursor = connections['so'].cursor()
            context.update(
                self.mount_context_and_print(
                    cursor, op, tam, cor, pula, qtd_lotes,
                    ultimo, ultima_cx, impresso, impresso_descr, obs1, obs2,
                    'print' in request.POST))
        context['form'] = form
        return render(request, self.template_name, context)
