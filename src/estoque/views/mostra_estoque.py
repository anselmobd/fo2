import datetime
import re
from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from geral.functions import has_permission, request_user
from utils.views import TableHfs, request_hash_trail, totalize_data

import produto.queries

from estoque import forms, queries
from estoque.functions import transfo2_num_doc, transfo2_num_doc_dt


class MostraEstoque(View):

    def __init__(self):
        self.Form_class = forms.MostraEstoqueForm
        self.template_name = 'estoque/mostra_estoque.html'
        self.title_name = 'Ajuste de estoque'
        self.table = TableHfs({
            'ref': ['Referência'],
            'cor': ['Cor'],
            'tam': ['Tamanho'],
            'qtd': ['Estoque atual', 'text-align: right;'],
            'qtd_inv': ['Estoque na data', 'text-align: right;'],
            'movimento': ['Movimento', 'text-align: right;'],
            'ajuste': ['Ajustar pelo inventário', 'text-align: right;'],
            'executa': ['Executa', 'text-align: right;'],
            'edita': ['Edita'],
            'item_no_tempo': ['No tempo', 'text-align: right;'],
        }, ['header', 'style'])

    def mount_context(
            self, request, cursor, deposito, ref, qtd, idata, hora, modelo):
        try:
            qtd = int(qtd)
        except Exception:
            qtd = None

        if modelo is None:
            modelo = '-'

        num_doc = transfo2_num_doc(idata, hora)
        context = {
            'deposito': deposito,
            'ref': ref,
            'qtd': qtd,
            'idata': idata,
            'hora': hora,
            'modelo': modelo,
            'num_doc': num_doc,
        }

        anterior = None
        posterior = None
        if modelo == '-':
            ref_modelo = re.search(r"\d+", ref)[0].lstrip('0')

            get_prox = False
            lista = queries.referencia_deposito(cursor, ref_modelo, deposito=deposito)
            for row in lista:
                item = row['ref']
                if get_prox:
                    posterior = item
                    break
                else:
                    if ref == item:
                        get_prox = True
                    else:
                        anterior = item
        else:
            if '-' in modelo:
                pass
            else:
                try:
                    imodelo = int(modelo)
                except Exception:
                    imodelo = None
                get_prox = False
                lista = produto.queries.busca_modelo(cursor)
                for row in lista:
                    item = row['modelo']
                    if get_prox:
                        posterior = item
                        break
                    else:
                        if imodelo == item:
                            get_prox = True
                        else:
                            anterior = item

        context.update({
            'anterior': anterior,
            'posterior': posterior,
        })

        # if idata is not None:
        #     data = queries.get_transfo2(cursor, deposito)
        #     if len(data) != 0:
        #         ult_num_doc = data[0]['numdoc']
        #         if int(num_doc) < ult_num_doc:
        #             ult_dt = transfo2_num_doc_dt(ult_num_doc)
        #             context.update(
        #                 {'erro':
        #                  'Data/Hora não pode ser anterior ao do último '
        #                  'inventário ({}: {})'.format(ult_num_doc, ult_dt)})
        #             return context

        data = queries.estoque_deposito_ref_modelo(
            cursor, deposito, ref, modelo)
        if len(data) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context

        for row in data:
            movimento = 0
            ajuste = 0
            if idata is not None:
                d_tot_movi = queries.get_transfo2_deposito_ref(
                    cursor, deposito, row['ref'], row['cor'], row['tam'],
                    tipo='s', data=idata, hora=hora)
                if len(d_tot_movi) != 0:
                    for d_row in d_tot_movi:
                        if d_row['es'] == 'E':
                            movimento += d_row['qtd']
                        elif d_row['es'] == 'S':
                            movimento -= d_row['qtd']
                if qtd is not None:
                    ajuste = qtd - row['qtd'] + movimento
            row['movimento'] = movimento
            row['qtd_inv'] = row['qtd'] - movimento
            row['ajuste'] = ajuste
            row['item_no_tempo'] = ''
            row['item_no_tempo|GLYPHICON'] = 'glyphicon-time'
            row['item_no_tempo|TARGET'] = '_BLANK'
            row['item_no_tempo|LINK'] = reverse(
                'estoque:item_no_tempo__get', args=[
                    row['ref'], row['cor'], row['tam'], deposito])

        if modelo == '-':
            self.table.cols('cor', 'tam')
        else:
            self.table.cols('ref', 'cor', 'tam')
        if idata is None:
            self.table.add('qtd')
        else:
            self.table.add('qtd_inv', 'movimento', 'qtd')
            if qtd is not None:
                self.table.add('ajuste')

        count_btn_executa = 0
        if has_permission(request, 'base.can_adjust_stock'):
            self.table.add('edita')

        self.table.add('item_no_tempo')

        if has_permission(request, 'base.can_adjust_stock'):
            if idata is not None and qtd is not None:
                self.table.add('executa')
            for row in data:
                movimento = 0
                if idata is not None:
                    d_tot_movi = queries.get_transfo2_deposito_ref(
                        cursor, deposito, row['ref'], row['cor'], row['tam'],
                        tipo='s', data=idata, hora=hora)
                    if len(d_tot_movi) != 0:
                        for d_row in d_tot_movi:
                            if d_row['es'] == 'E':
                                movimento += d_row['qtd']
                            elif d_row['es'] == 'S':
                                movimento -= d_row['qtd']
                row['movimento'] = movimento
                row['qtd_inv'] = row['qtd'] - movimento
                row['edita'] = 'Edita'
                row['edita|LINK'] = reverse(
                    'estoque:edita_estoque__get', args=[
                        deposito, row['ref'], row['cor'], row['tam']])
                if idata is not None and qtd is not None:
                    if row['ajuste'] == 0:
                        row['executa'] = '-'
                    else:
                        count_btn_executa += 1
                        trail = request_hash_trail(
                            request,
                            deposito,
                            row['ref'],
                            row['cor'],
                            row['tam'],
                            row['ajuste'],
                        )
                        row['executa'] = '''
                            <a title="Executa ajuste indicado pelo inventário"
                             class="btn btn-primary exec_ajuste"
                             style="padding: 0px 12px;"
                             href="javascript:void(0);"
                             onclick="exec_ajuste(this,
                                \'{ajuste}\', \'{link}\');"
                            >Ajusta</a>
                        '''.format(
                            dep=deposito,
                            ref=row['ref'],
                            cor=row['cor'],
                            tam=row['tam'],
                            ajuste=row['ajuste'],
                            trail=trail,
                            link=reverse(
                                'estoque:executa_ajuste', args=[
                                    deposito,
                                    row['ref'],
                                    row['cor'],
                                    row['tam'],
                                    row['ajuste'],
                                    num_doc,
                                    trail,
                                ]
                            )
                        )

        headers, fields, style = self.table.hfs()
        totalize_data(data, {
            'sum': ['qtd_inv', 'movimento', 'qtd'],
            'count': [],
            'descr': {'tam': 'Totais:'},
            'row_style': 'font-weight: bold;',
            })

        context.update({
            'safe': ['executa'],
            'headers': headers,
            'fields': fields,
            'data': data,
            'style': style,
            'count_btn_executa': count_btn_executa,
        })

        data = queries.get_transfo2_deposito_ref(cursor, deposito, ref)
        for row in data:
            if row['numdoc'] == 702000000:
                row['dh_inv'] = '-'
            else:
                row['dh_inv'] = transfo2_num_doc_dt(row['numdoc'])
        if len(data) != 0:
            context.update({
                't_headers': ['Data/hora', 'Documento', 'Data/hora inventário',
                              'Cor', 'Tamanho', 'Transação', 'E/S',
                              'Quantidade'],
                't_fields': ['hora', 'numdoc', 'dh_inv',
                             'cor', 'tam', 'trans', 'es',
                             'qtd'],
                't_data': data,
                't_style': {8: 'text-align: right;', },
            })
        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}

        get_data_inv = None
        idata = None
        if 'ajuste_inv_data' in request.COOKIES:
            get_data_inv = request.COOKIES.get('ajuste_inv_data')
        if get_data_inv is None:
            self.form = self.Form_class()
        else:
            self.form = self.Form_class(initial={"data": get_data_inv})
            idata = datetime.datetime.strptime(get_data_inv, '%Y-%m-%d').date()

        deposito = kwargs['deposito']
        ref = kwargs['ref']
        modelo = kwargs['modelo']
        cursor = db_cursor_so(request)
        context.update(self.mount_context(
            request, cursor, deposito, ref, None, idata, None, modelo))

        context['form'] = self.form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        self.form = self.Form_class(request.POST)

        deposito = kwargs['deposito']
        ref = kwargs['ref']
        modelo = kwargs['modelo']

        set_data_inv = None
        if self.form.is_valid():
            qtd = self.form.cleaned_data['qtd']
            data = self.form.cleaned_data['data']
            hora = self.form.cleaned_data['hora']
            set_data_inv = data
            cursor = db_cursor_so(request)
            context.update(self.mount_context(
                request, cursor, deposito, ref, qtd, data, hora, modelo))

        context['form'] = self.form
        response = render(request, self.template_name, context)
        if set_data_inv is None:
            response.delete_cookie('ajuste_inv_data')
        else:
            response.set_cookie('ajuste_inv_data', set_data_inv)
        return response
