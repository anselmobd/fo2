from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.views import View
from django.urls import reverse

from fo2.connections import db_cursor_so

from utils.views import group_rowspan

import cd.forms
from cd.queries.novo_modulo.grade_cd import (
    grade_estoque,
    refs_em_estoque,
)


class GradeEstoqueTotais(PermissionRequiredMixin, View):

    def __init__(self):
        self.permission_required = 'cd.can_view_grades_estoque'
        self.template_name = 'cd/novo_modulo/grade_estoque_totais.html'

    def mount_context(self):
        inventario = grade_estoque(self.cursor, tipo='i')
        referencias = refs_em_estoque(self.cursor_s, get='ref')
        pprint(inventario)

    def get(self, request, *args, **kwargs):
        self.cursor = db_cursor_so(request)
        self.page = request.GET.get('page', 1)
        self.context = {}
        self.mount_context()
        return render(request, self.template_name, self.context)
