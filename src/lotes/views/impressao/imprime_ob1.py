import re
from datetime import datetime
from pprint import pprint

from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from fo2.connections import db_cursor_so

from utils.classes import TermalPrint

import lotes.queries.ob
import lotes.queries.os
import lotes.models as models
import lotes.queries as queries
from lotes.forms.impressao import ImprimeOb1Form


class ImprimeOb1(LoginRequiredMixin, View):

    def __init__(self):
        super().__init__()
        self.login_url = '/intradm/login/'
        self.Form_class = ImprimeOb1Form
        self.template_name = 'lotes/impressao/imprime_ob1.html'
        self.title_name = 'Imprime etiqueta de OB1'

    def mount_context_and_print(self, cursor, os, caixa_inicial, caixa_final, do_print):
        context = {
            'os': os,
            'caixa_inicial': caixa_inicial,
            'caixa_final': caixa_final,
        }

        caixa_inicial_val = caixa_inicial or 0
        caixa_final_val = caixa_final or 99999

        op_data = lotes.queries.os.os_op(cursor, os)
        if len(op_data) == 0:
            context.update({
                'msg_erro': 'Nehuma OP relaconada a OS',
            })
            return context

        if len(op_data) > 1:
            context.update({
                'msg_erro': 'Mais de 1 OP relaconada a OS',
            })
            return context

        op = op_data[0]['OP']

        o_data = queries.ob.get_ob(cursor, os)
        if len(o_data) == 0:
            context.update({
                'msg_erro': 'Nehuma OB selecionada',
            })
            return context

        data = []
        for row in o_data:
            row['op'] = op
            row['os'] = os
            obs_aux = row['observacao'].split('.')[1]
            row['caixa'] = int(obs_aux.split()[0])
            if caixa_inicial_val <= row['caixa']:
                if row['caixa'] <= caixa_final_val:
                    data.append(row)

        context.update({
            'count': len(data),
            'headers': ('OP', 'OS', 'Caixa', 'OB'),
            'fields': ('op', 'os', 'caixa', 'ob'),
            'data': data,
        })

        if do_print:
            try:
                impresso = models.Impresso.objects.get(
                    nome='Etiqueta OB1')
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
            teg = TermalPrint(
                usuario_impresso.impressora_termica.nome,
                file_dir="impresso/ob1/%Y/%m"
            )
            teg.template(usuario_impresso.modelo.gabarito, '\r\n')
            teg.printer_start()
            try:
                for row in data:
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
            os = form.cleaned_data['os']
            caixa_inicial = form.cleaned_data['caixa_inicial']
            caixa_final = form.cleaned_data['caixa_final']

            cursor = db_cursor_so(request)
            context.update(
                self.mount_context_and_print(
                    cursor, os, caixa_inicial, caixa_final,
                    'print' in request.POST))
        context['form'] = form
        return render(request, self.template_name, context)
