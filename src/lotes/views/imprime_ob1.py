import re
from datetime import datetime
from pprint import pprint

from django.shortcuts import render
from django.db import connections
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from utils.classes import TermalPrint

from lotes.forms import ImprimeOb1Form
import lotes.queries.ob
import lotes.models as models
import lotes.queries as queries


class ImprimeOb1(LoginRequiredMixin, View):
    login_url = '/intradm/login/'
    Form_class = ImprimeOb1Form
    template_name = 'lotes/imprime_ob1.html'
    title_name = 'Imprime etiqueta de OB1'

    def mount_context_and_print(self, cursor, os, caixa_inicial, caixa_final, do_print):
        context = {}

        caixa_inicial_val = caixa_inicial or 0
        caixa_final_val = caixa_final or 99999

        data = queries.ob.get_ob(
            cursor, os, caixa_inicial_val, caixa_final_val)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nehuma OB selecionada',
            })
            return context

        for row in data:
            row['os'] = os
            row['caixa'] = row['observacao'].split('.')[1]

        context.update({
            'count': len(data),
            'os': os,
            'caixa_inicial': caixa_inicial,
            'caixa_final': caixa_final,
            'headers': ('OS', 'Caixa'),
            'fields': ('os', 'caixa'),
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
            teg = TermalPrint(usuario_impresso.impressora_termica.nome)
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

            cursor = connections['so'].cursor()
            context.update(
                self.mount_context_and_print(
                    cursor, os, caixa_inicial, caixa_final,
                    'print' in request.POST))
        context['form'] = form
        return render(request, self.template_name, context)
