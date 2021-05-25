from pprint import pprint

from django.shortcuts import render
from django.db.models import Count
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from fo2.connections import db_cursor_so

from utils.classes import TermalPrint

import lotes.forms
import lotes.functions
import lotes.queries.op
import lotes.queries.lote
import lotes.models as models


class ImprimeCaixaLotes(LoginRequiredMixin, View):
    login_url = '/intradm/login/'
    Form_class = lotes.forms.ImprimeCaixaLotesForm
    template_name = 'lotes/imprime_caixa_lotes.html'
    title_name = 'Etiqueta de caixa lotes'
    impresso_slug = "etiqueta-de-caixa-com-barras-de-n-lotes"

    def mount_context_and_print(
            self, cursor, op, tam, cor, parm_pula, parm_qtd_lotes,
            ultimo, ultima_cx, obs1, obs2, do_print):

        if not lotes.functions.lotes_em_caixa(self, cursor, op):
            return

        data = self.context['data']
        lotes_caixa = self.context['lotes_caixa']
        ref = self.context['ref']
        descr_ref = self.context['descr_ref']

        header_lotes_caixa = []
        field_lotes_caixa = []
        dict_lotes_caixa = {}
        for i in range(1,lotes_caixa+1):
            f_lote = f'lote{i}'
            f_qtd = f'qtd{i}'
            dict_lotes_caixa[f_lote] = ""
            dict_lotes_caixa[f_qtd] = ""
            header_lotes_caixa.append(f'Lote {i}')
            header_lotes_caixa.append(f'Qtd. {i}')
            field_lotes_caixa.append(f_lote)
            field_lotes_caixa.append(f_qtd)

        l_data = []
        for row in data:
            n_lote_caixa = row['n_lote_caixa']
            if n_lote_caixa == 1:
                l_row = {
                    'lotes_caixa': lotes_caixa,
                    'cor': row['cor'],
                    'data_entrada_corte': row['data_entrada_corte'],
                    'descr_cor': row['descr_cor'],
                    'descr_referencia': row['descr_referencia'],
                    'descr_tamanho': row['descr_tamanho'],
                    'narrativa': row['narrativa'],
                    'op': row['op'],
                    'pacote': row['caixa_ct'],
                    'ref': row['ref'],
                    'situacao': row['situacao'],
                    'tam': row['tam'],
                    'tamord': row['ordem_tamanho'],
                    'qtd_cortam': str(row['total_cx_ct']),
                    'cont_cortam': str(row['caixa_ct']),
                    'cx_ct': f"{row['caixa_ct']} / {row['total_cx_ct']}",
                    'cx_op': f"{row['caixa_op']} / {row['total_cx_op']}",
                    'lote_count': row['qtd_lote_caixa'],
                    'narrativa': ' '.join((
                        row['descr_referencia'],
                        row['descr_cor'],
                        row['descr_tamanho'])),
                    'narrativa_ct': ' '.join((
                        row['descr_cor'],
                        row['descr_tamanho'])),
                    'qtd_pcs_cx': row['qtd_caixa'],
                    'prim': '*' if row['caixa_ct'] == 1 else ''
                }
                l_row.update(dict_lotes_caixa)
                l_data.append(l_row)
            else:
                l_row = l_data[-1]
            f_lote = f'lote{n_lote_caixa}'
            f_qtd = f'qtd{n_lote_caixa}'
            l_row[f_lote] = row['lote']
            l_row[f_qtd] = row['qtd']
    
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
                pula_lote = row['cont_total'] != ultima_cx
                for i in range(1,lotes_caixa+1):
                    f_lote = f'lote{i}'
                    if f_lote in row:
                        pula_lote = pula_lote and row[f_lote] != ultimo
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
            self.context.update({
                'msg_erro': 'Nehum lote selecionado',
            })
            return

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

        headers = [
            'CX.OP', 'Cor', 'Tamanho', 'Narrativa', '1º', 'CX.Cor/Tam']
        headers += header_lotes_caixa
        headers += ['Qtd. Caixa']

        fields = ['cx_op', 'cor', 'tam', 'narrativa_ct', 'prim', 'cx_ct']
        fields += field_lotes_caixa
        fields += ['qtd_pcs_cx']

        # prepara dados selecionados
        self.context.update({
            'count': len(data),
            'op': op,
            'ref': ref,
            'descr_ref': descr_ref,
            'op_mae': op_mae,
            'ref_mae': ref_mae,
            'cor': cor,
            'tam': tam,
            'ultima_cx': ultima_cx,
            'ultimo': ultimo,
            'pula': parm_pula,
            'qtd_lotes': parm_qtd_lotes,
            'headers': headers,
            'fields': fields,
            'data': data,
        })

        if do_print:
            try:
                impresso = models.Impresso.objects.get(
                    slug=self.impresso_slug)
                self.context.update({
                    'cod_impresso': impresso.nome,
                })
            except models.Impresso.DoesNotExist:
                self.context.update({
                    "msg_erro": f"Impresso '{self.impresso_slug}'não cadastrado",
                })
                do_print = False

        if do_print:
            try:
                usuario_impresso = models.UsuarioImpresso.objects.get(
                    usuario=self.request.user, impresso=impresso)
            except models.UsuarioImpresso.DoesNotExist:
                usuario_impresso = None
            if usuario_impresso is None:
                self.context.update({
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

        return

    def get(self, request):
        self.context = {'titulo': self.title_name}
        form = self.Form_class()
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.request = request
        self.context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            op = form.cleaned_data['op']
            tam = form.cleaned_data['tam']
            cor = form.cleaned_data['cor']
            pula = form.cleaned_data['pula']
            qtd_lotes = form.cleaned_data['qtd_lotes']
            ultimo = form.cleaned_data['ultimo']
            ultima_cx = form.cleaned_data['ultima_cx']
            obs1 = form.cleaned_data['obs1']
            obs2 = form.cleaned_data['obs2']

            cursor = db_cursor_so(request)
            self.mount_context_and_print(
                cursor, op, tam, cor, pula, qtd_lotes,
                ultimo, ultima_cx, obs1, obs2,
                'print' in request.POST)
        self.context['form'] = form
        return render(request, self.template_name, self.context)
