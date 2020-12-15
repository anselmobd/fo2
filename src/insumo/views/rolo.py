from pprint import pprint

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connections
from django.shortcuts import render, redirect
from django.views import View

import insumo.forms
import insumo.queries


class Rolo(View):
    Form_class = insumo.forms.RoloForm
    template_name = 'insumo/rolo.html'
    title_name = 'Rolo'

    def mount_context(
            self, cursor, rolo, sit, ref, cor, op, est_res, est_aloc, est_conf, page):

        linhas_pagina = 100

        rolo_estoque_dict = {
            0: 'Em produção',
            1: 'Em estoque',
            2: 'Faturado ou fora do estoque',
            3: 'Relacionado a pedido',
            4: 'Em trânsito',
            5: 'Coletado',
            7: 'Relacionado a ordem de serviço',
            8: 'Rolo com nota emitida em processo de cancelamento',
        }

        est_res_dict = {
            'S': 'Reservado',
            'N': 'Não reservado',
        }

        est_aloc_dict = {
            'S': 'Alocado',
            'N': 'Não alocado',
        }

        est_conf_dict = {
            'S': 'Confirmado',
            'N': 'Não confirmado',
        }

        context = {
            'rolo': rolo,
            'sit': sit,
            'sit_descr': '' if sit == '' else rolo_estoque_dict[int(sit)],
            'ref': ref,
            'cor': cor,
            'op': op,
            'est_res': est_res,
            'est_res_descr': '' if est_res == '' else est_res_dict[est_res],
            'est_aloc': est_aloc,
            'est_aloc_descr': '' if est_aloc == '' else est_aloc_dict[est_aloc],
            'est_conf': est_conf,
            'est_conf_descr': '' if est_conf == '' else est_conf_dict[est_conf],
            'linhas_pagina': linhas_pagina,
            'paginas_vizinhas': 5,
        }

        data = insumo.queries.rolo_inform(
            cursor, rolo, sit, ref, cor, op, est_res, est_aloc, est_conf)
        paginator = Paginator(data, linhas_pagina)
        try:
            data = paginator.page(page)
        except PageNotAnInteger:
            data = paginator.page(1)
        except EmptyPage:
            data = paginator.page(paginator.num_pages)

        for row in data:
            row['dt_entr'] = row['dt_entr'].date()
            row['sit|HOVER'] = rolo_estoque_dict[row['sit']]
            if row['op'] == None:
                row['op'] = '-'
                row['dt_reserva'] = '-'
                row['u_reserva'] = '-'
            else:
                row['dt_reserva'] = row['dt_reserva'].date()
            if row['conf'] == None:
                row['conf'] = 'N'
                row['op_aloc'] = '-'
            else:
                row['conf'] = 'S'
            if row['dh_conf'] == None:
                row['u_conf'] = '-'
                row['dh_conf'] = '-'

        context.update({
            'headers': ('Rolo', 'Entrada', 'Nível', 'Referência',
                        'Cor', 'Tamanho', 'Situação',
                        'Reservado', 'OP', 'Usuário',
                        'Alocado', 'OP', 'Confirmado', 'Usuário'),
            'fields': ('rolo', 'dt_entr', 'nivel', 'ref',
                       'cor', 'tam', 'sit',
                       'dt_reserva', 'op', 'u_reserva',
                       'conf', 'op_aloc', 'dh_conf', 'u_conf'),
            'data': data,
        })

        return context

    def get(self, request, *args, **kwargs):
        if 'rolo' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'rolo' in kwargs:
            form.data['rolo'] = kwargs['rolo']
        if form.is_valid():
            rolo = form.cleaned_data['rolo']
            sit = form.cleaned_data['sit']
            ref = form.cleaned_data['ref']
            cor = form.cleaned_data['cor']
            op = form.cleaned_data['op']
            est_res = form.cleaned_data['est_res']
            est_aloc = form.cleaned_data['est_aloc']
            est_conf = form.cleaned_data['est_conf']
            page = form.cleaned_data['page']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(
                cursor, rolo, sit, ref, cor, op, est_res, est_aloc, est_conf, page))
        context['form'] = form
        return render(request, self.template_name, context)
