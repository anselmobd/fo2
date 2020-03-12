from pprint import pprint
import re
import datetime
from datetime import timedelta
from pytz import utc

from django.db import IntegrityError
from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connections, connection
from django.db.models import Count, Sum, Q, Value
from django.db.models.functions import Coalesce, Substr
from django.contrib.auth.mixins \
    import PermissionRequiredMixin, LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from django.urls import reverse
from django.http import JsonResponse
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import User

from utils.functions.models import rows_to_dict_list_lower, GradeQtd
from utils.views import totalize_grouped_data, group_rowspan
import lotes.models
from geral.functions import request_user, has_permission

import cd.queries as queries
import cd.forms


def index(request):
    return render(request, 'cd/index.html')


def teste_som(request):
    context = {}
    return render(request, 'cd/teste_som.html', context)


class Historico(View):

    def __init__(self):
        self.Form_class = cd.forms.HistoricoForm
        self.template_name = 'cd/historico.html'
        self.title_name = 'Histórico de OP'

    def mount_context(self, cursor, op):
        context = {
            'op': op,
            }

        data = queries.historico(cursor, op)
        if len(data) == 0:
            context.update({'erro': 'Sem lotes ativos'})
            return context
        for row in data:
            if row['dt'] is None:
                row['dt'] = 'Nunca inventariado'
            if row['endereco'] is None:
                if row['usuario'] is None:
                    row['endereco'] = '-'
                else:
                    row['endereco'] = 'SAIU!'
            if row['usuario'] is None:
                row['usuario'] = '-'
        context.update({
            'headers': ('Data', 'Qtd. de lotes', 'Endereço', 'Usuário'),
            'fields': ('dt', 'qtd', 'endereco', 'usuario'),
            'data': data,
        })

        data = queries.historico_detalhe(cursor, op)
        for row in data:
            if row['dt'] is None:
                row['dt'] = 'Nunca inventariado'
            if row['endereco'] is None:
                if row['usuario'] is None:
                    row['endereco'] = '-'
                else:
                    row['endereco'] = 'SAIU!'
            if row['usuario'] is None:
                row['usuario'] = '-'
            row['lote|LINK'] = reverse(
                'cd:historico_lote', args=[row['lote']])
        context.update({
            'd_headers': ('Lote', 'Última data', 'Endereço', 'Usuário'),
            'd_fields': ('lote', 'dt', 'endereco', 'usuario'),
            'd_data': data,
        })

        return context

    def get(self, request, *args, **kwargs):
        if 'op' in kwargs and kwargs['op'] is not None:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'op' in kwargs and kwargs['op'] is not None:
            form.data['op'] = kwargs['op']
        if form.is_valid():
            op = form.cleaned_data['op']
            cursor = connection.cursor()
            context.update(self.mount_context(cursor, op))
        context['form'] = form
        return render(request, self.template_name, context)


class HistoricoLote(View):

    def __init__(self):
        self.Form_class = cd.forms.ALoteForm
        self.template_name = 'cd/historico_lote.html'
        self.title_name = 'Histórico de lote'

    def mount_context(self, cursor, lote):
        context = {
            'lote': lote,
            }

        data = queries.historico_lote(cursor, lote)
        if len(data) == 0:
            context.update({'erro': 'Lote não encontrado ou nunca endereçado'})
            return context

        lote_cd = lotes.models.Lote.objects.get(lote=lote)
        op = str(lote_cd.op)
        context.update({
            'op': op,
        })

        old_estagio = None
        old_usuario = None
        old_local = None
        for row in data:
            n_info = 0
            log = row['log']
            log = log.replace("<UTC>", "utc")
            log = re.sub(
                r'^(.*)<SimpleLazyObject: <User: ([^\s]*)>>(.*)$',
                r'\1"\2"\3', log)
            log = re.sub(
                r'^(.*)<User: ([^\s]*)>(.*)$',
                r'\1"\2"\3', log)
            dict_log = eval(log)

            if 'estagio' in dict_log:
                row['estagio'] = dict_log['estagio']
                old_estagio = row['estagio']
                n_info += 1
            else:
                if old_estagio is None:
                    row['estagio'] = '-'
                else:
                    row['estagio'] = '='
            if row['estagio'] == 999:
                row['estagio'] = 'Finalizado'

            if 'local' in dict_log:
                row['local'] = dict_log['local']
                old_local = row['local']
                n_info += 1
            else:
                if old_local is None:
                    row['local'] = '-'
                else:
                    row['local'] = '='
            if row['local'] is None:
                row['local'] = 'SAIU!'

            if 'local_usuario' in dict_log:
                row['local_usuario'] = dict_log['local_usuario']
                old_usuario = row['local_usuario']
                n_info += 1
            else:
                if old_usuario is None or row['local'] in ('-', '='):
                    row['local_usuario'] = '-'
                else:
                    row['local_usuario'] = '='

            row['n_info'] = n_info

        context.update({
            'headers': ('Data', 'Estágio', 'Local', 'Usuário'),
            'fields': ('time', 'estagio', 'local', 'local_usuario'),
            'data': [row for row in data if row['n_info'] != 0],
        })

        return context

    def get(self, request, *args, **kwargs):
        if 'lote' in kwargs and kwargs['lote'] is not None:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'lote' in kwargs and kwargs['lote'] is not None:
            form.data['lote'] = kwargs['lote']
        if form.is_valid():
            lote = form.cleaned_data['lote']
            cursor = connection.cursor()
            context.update(self.mount_context(cursor, lote))
        context['form'] = form
        return render(request, self.template_name, context)
