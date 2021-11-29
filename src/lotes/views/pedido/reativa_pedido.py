from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.views import View

from fo2.connections import db_cursor_so

from lotes.queries.pedido.reativa_pedido import exec_reativa_pedido


class ReativaPedido(PermissionRequiredMixin, View):

    def __init__(self):
        self.permission_required = 'lotes.can_reactivate_pedido'

    def get(self, request, *args, **kwargs):
        cursor = db_cursor_so(request)
        pedido = kwargs['pedido']
        exec_reativa_pedido(cursor, pedido)
        return redirect('producao:pedido__get', pedido)
