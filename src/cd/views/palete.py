from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.views import View


class Palete(PermissionRequiredMixin, View):

    def __init__(self, mobile=False):
        self.permission_required = 'lotes.can_relocate_lote'
        # self.Form_class = cd.forms.TrocaEnderecoForm
        self.template_name = 'cd/troca_endereco.html'
        self.title_name = 'Trocar endereço'

