from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.views import View


class ListaMovimentos(View):

    Form_class = forms.ListaMovimentosForm
    template_name = 'estoque/lista_movs.html'
    title_name = 'Lista de movimentações de estoque'
