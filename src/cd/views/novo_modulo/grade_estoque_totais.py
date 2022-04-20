from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.views import View
from django.urls import reverse

from fo2.connections import db_cursor_so

from utils.views import group_rowspan

from base.paginator import paginator_basic
from utils.functions.strings import only_digits

import cd.forms
from cd.queries.novo_modulo.lotes import lotes_em_estoque


class GradeEstoqueTotais(PermissionRequiredMixin, View):

    def __init__(self):
        self.permission_required = 'cd.can_view_grades_estoque'
        self.template_name = 'cd/novo_modulo/grade_estoque_totais.html'

    def mount_context(self):
        inventario = lotes_em_estoque(self.cursor, get='ref')
        modelos = set([
            int(only_digits(r['ref']))
            for r in inventario
        ])
        modelos = sorted(modelos)
        data = [
            {'modelo': m}
            for m in modelos
        ]

        data = paginator_basic(data, 10, self.page)

        headers = ['Modelo']
        fields = ['modelo']
        self.context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
        })

    def get(self, request, *args, **kwargs):
        self.cursor = db_cursor_so(request)
        self.page = request.GET.get('page', 1)
        self.context = {}
        self.mount_context()
        return render(request, self.template_name, self.context)
