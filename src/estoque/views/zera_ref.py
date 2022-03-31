from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.views import View

from fo2.connections import db_cursor_so

__all__ = ['ZeraRef']


class ZeraRef(PermissionRequiredMixin, View):
    
    def __init__(self):
        self.permission_required = 'estoque.pode_zerar_depositos'

    def get(self, request, **kwargs):
        self.request = request
        self.data = kwargs
        self.cursor = db_cursor_so(request)

        return JsonResponse(self.data, safe=False)
