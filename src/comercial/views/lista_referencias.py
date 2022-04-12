from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View


import comercial.forms as forms
import comercial.queries as queries


class ListaReferencias(View):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template_name = 'comercial/lista_referencias.html'
        self.context = {'titulo': 'Lista referências'}

    def mount_context(self):
        pass

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)
