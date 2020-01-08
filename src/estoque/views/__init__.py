import datetime
import time
import re
import hashlib
from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.views import View
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.shortcuts import redirect
from django.core.exceptions import SuspiciousOperation

from utils.views import (
    totalize_data, totalize_grouped_data, TableHfs, request_hash_trail)
from fo2.template import group_rowspan
from geral.functions import request_user, has_permission
import produto.queries

from estoque import forms
from estoque import models
from estoque import queries
from estoque.classes import TransacoesDeAjuste
from estoque.functions import transfo2_num_doc, transfo2_num_doc_dt

from .executa_ajuste import *
from .edita_estoque import *
from .mostra_estoque import *
from .posicao_estoque import *
from .referencia_deposito import *
from .valor_mp import *


def index(request):
    return render(request, 'estoque/index.html')


class EstoqueNaData(View):
    pass


class RefsComMovimento(View):
    Form_class = forms.InventarioExpedicaoForm
    template_name = 'estoque/refs_com_movimento.html'
    title_name = 'Referências com movimento'

    def mount_context(self, cursor, data_ini):
        context = {
            'data_ini': data_ini,
        }

        refs = queries.refs_com_movimento(cursor, data_ini)
        if len(refs) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context

        deps = [231, 101, 102]
        for ref in refs:
            ref['deps'] = []
            for dep in deps:
                header, fields, data, style, total = \
                    queries.grade_estoque(
                        cursor, ref['ref'], dep, data_ini=data_ini)
                grade = None
                if total != 0:
                    grade = {
                        'headers': header,
                        'fields': fields,
                        'data': data,
                        'style': style,
                    }
                    ref['deps'].append({
                        'dep': dep,
                        'grade': grade,
                    })

        context.update({
            'headers': ['Referência'],
            'fields': ['ref'],
            'refs': refs,
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            data_ini = form.cleaned_data['data_ini']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, data_ini))
        context['form'] = form
        return render(request, self.template_name, context)
