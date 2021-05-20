from pprint import pprint

from django.shortcuts import render
from django.db.models import Count
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from fo2.connections import db_cursor_so

from utils.classes import TermalPrint

from lotes.forms import ImprimePacote3LotesForm
import lotes.queries.op
import lotes.queries.lote
import lotes.models as models


class ImprimeCaixaLotes(LoginRequiredMixin, View):
    login_url = '/intradm/login/'
    Form_class = ImprimePacote3LotesForm
    template_name = 'lotes/imprime_pacote3lotes.html'
    title_name = 'Etiqueta de caixa lotes'

    def mount_context_and_print(
            self, cursor, op, tam, cor, parm_pula, parm_qtd_lotes,
            ultimo, ultima_cx, impresso, impresso_descr, obs1, obs2, do_print):

        context = {}

        # Pacotes de 3 Lotes
        l_data = lotes.queries.op.caixas_op_3lotes(cursor, op)

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

        if ref[0] < 'C':
            context.update({
                'msg_erro': 'Etiqueta de caixa deve ser utilizada para MD',
            })
            l_data = []
            return context

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
            row['narrativa'] = ' '.join((
                row['descr_referencia'],
                row['descr_cor'],
                row['descr_tamanho']))
            row['qtd_total'] = '{}'.format(qtd_total)
            row['qtd_pcs_cx'] = row['qtd1']
            cont_total += 1
            row['cont_total'] = '{}'.format(cont_total)
            row['cx_op'] = '{} / {}'.format(cont_total, qtd_total)

            row['qtd_lotes'] = '1'
            if row['oc2']:
                row['qtd_lotes'] = '2'
                row['qtd_pcs_cx'] += row['qtd2']
            else:
                row['oc2'] = ''
                row['qtd2'] = ''
            if row['oc3']:
                row['qtd_lotes'] = '3'
                row['qtd_pcs_cx'] += row['qtd3']
            else:
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
        opi_data = lotes.queries.op.op_inform(cursor, op)
        opi_row = opi_data[0]
        op_mae = ''
        ref_mae = ''
        if opi_row['TIPO_FM_OP'] == 'Filha de':
            op_mae = '{}'.format(opi_row['OP_REL'])
            opmaei_data = lotes.queries.op.op_inform(cursor, op_mae)
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
            'headers': ('CX.OP', 'Cor', 'Tamanho', 'Narrativa',
                        '1º', 'CX.Cor/Tam',
                        'Lote 1', 'Qtd. 1', 'Lote 2', 'Qtd. 2',
                        'Lote 3', 'Qtd. 3', 'Qtd. Caixa'),
            'fields': ('cx_op', 'cor', 'tam', 'narrativa',
                       'prim', 'cx_ct',
                       'lote1', 'qtd1', 'lote2', 'qtd2',
                       'lote3', 'qtd3', 'qtd_pcs_cx'),
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

            cursor = db_cursor_so(request)
            context.update(
                self.mount_context_and_print(
                    cursor, op, tam, cor, pula, qtd_lotes,
                    ultimo, ultima_cx, impresso, impresso_descr, obs1, obs2,
                    'print' in request.POST))
        context['form'] = form
        return render(request, self.template_name, context)
