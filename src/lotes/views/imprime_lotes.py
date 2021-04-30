import re
from datetime import datetime
from pprint import pprint

from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from fo2.connections import db_cursor_so

from utils.classes import TermalPrint

from lotes.forms import ImprimeLotesForm
import lotes.queries.op
import lotes.models as models
import lotes.queries as queries


class ImprimeLotes(LoginRequiredMixin, View):
    login_url = '/intradm/login/'
    Form_class = ImprimeLotesForm
    template_name = 'lotes/imprime_lotes.html'
    title_name = 'Imprime "Cartela de Lote"'

    def est_list(self, est):
        estagios = est.split(' & ')
        estList = []
        for estagio in estagios:
            estList.append(re.sub(r'^([1234567890]+).*$', r'\1', estagio))
        return estList

    def mount_context_and_print(self, cursor, op, estagio, tam, cor, order,
                                oc_inicial, oc_final,
                                pula, qtd_lotes, ultimo,
                                impresso, order_descr, obs1, obs2, do_print):
        context = {}

        oc_inicial_val = oc_inicial or 0
        oc_final_val = oc_final or 99999

        seq_est = queries.op.get_seq_est_op(cursor, op)
        dict_est_seq = {se['est']: se['seq'] for se in seq_est}
        dict_est_seq[9999] = 9999  # Finalizado
        tem_est6 = 6 in dict_est_seq

        # Lotes ordenados por OC
        l_data = queries.lote.get_imprime_lotes(
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

        lote_ate_est6 = 0
        pula_lote = ultimo != ''
        data = []
        for row in l_data:
            row['num_lote'] = '{}/{}'.format(row['nlote'], row['totlotes'])
            row['datahora'] = format(datetime.now(), '%d/%m/%y %H:%M')
            row['qtdtot'] = None
            row['parcial'] = None
            row['narrativa'] = ' '.join((
                row['descr_referencia'],
                row['descr_cor'],
                row['descr_tamanho']))
            row['lote'] = '{}{:05}'.format(row['periodo'], row['oc'])
            if row['oc'] == row['oc1']:
                row['prim'] = '*'
            else:
                row['prim'] = ''
            if row['divisao'] is None:
                row['descricao_divisao'] = ''
            if tem_est6:
                if dict_est_seq[row['est_num']] <= dict_est_seq[6]:
                    lote_ate_est6 += 1
                    continue
            if pula_lote:
                pula_lote = row['lote'] != ultimo
            else:
                if estagio == '':
                    row['qtd_tela'] = row['qtd']
                    data.append(row)
                else:
                    estagios = self.est_list(row['est'])
                    quants = row['quants'].split(';')
                    if estagio in estagios:
                        iestagio = estagios.index(estagio)
                        do_append = False
                        if len(quants) > (iestagio+1):
                            do_append = True
                        else:
                            totquants = 0
                            for q in [int(x) for x in quants]:
                                totquants += q
                            if totquants < row['qtd']:
                                do_append = True
                        if do_append:
                            row['parcial'] = True
                            row['qtdtot'] = row['qtd']
                            row['estagio'] = estagio
                            row['qtd'] = quants[iestagio]
                            row['qtd_tela'] = '{} ({})'.format(
                                row['qtd'], row['qtdtot'])
                            data.append(row)

        context.update({
            'lote_ate_est6': lote_ate_est6,
        })
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nehum lote selecionado',
            })
            return context

        ref = l_data[0]['ref']

        # busca informação de OP mãe
        opi_data = lotes.queries.op.op_inform(cursor, op)
        opi_row = opi_data[0]
        op_mae = ''
        ref_mae = ''
        if opi_row['TIPO_FM_OP'] == 'Filha de':
            op_mae = opi_row['OP_REL']
            opmaei_data = lotes.queries.op.op_inform(cursor, op_mae)
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
            'estagio': estagio,
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
            'headers': ('Tamanho', 'Cor', 'Narrativa',
                        'Período', 'OC', '1º', 'Quant.',
                        'Lote', 'Estágio', 'Unidade', '#'),
            'fields': ('tam', 'cor', 'narrativa',
                       'periodo', 'oc', 'prim', 'qtd_tela',
                       'lote', 'est', 'descricao_divisao', 'num_lote'),
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
            e_data = lotes.queries.op.op_estagios(cursor, op)
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
                    try:
                        teg.printer_send()
                    except Exception as e:
                        context.update({
                            'msg_erro': f'Erro ao imprimir <{e}>',
                        })
                        return context
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
            estagio = form.cleaned_data['estagio']
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

            cursor = db_cursor_so(request)
            context.update(
                self.mount_context_and_print(
                    cursor, op, estagio, tam, cor, order, oc_inicial, oc_final,
                    pula, qtd_lotes, ultimo, impresso, order_descr, obs1, obs2,
                    'print' in request.POST))
        context['form'] = form
        return render(request, self.template_name, context)
