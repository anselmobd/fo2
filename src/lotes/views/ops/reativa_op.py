from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.views import View

from fo2.connections import db_cursor_so

import lotes.queries.op


class ReativaOp(PermissionRequiredMixin, View):

    def __init__(self):
        self.permission_required = 'lotes.can_repair_seq_op'

    def get(self, request, *args, **kwargs):
        cursor = db_cursor_so(request)
        op = kwargs['op']
        lotes.queries.op.reativa_op.reativa_op(cursor, op)
        return redirect('producao:op__get', op)
