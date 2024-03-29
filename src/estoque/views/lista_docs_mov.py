from pprint import pprint

from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from utils.functions.views import Fo2ViewMethods

from estoque import forms, models


class ListaDocsMovimentacao(View, Fo2ViewMethods):

    def __init__(self):
        super().__init__()
        self.Form_class = forms.ListaDocsMovimentacaoForm
        self.template_name = 'estoque/lista_docs_mov.html'
        self.title_name = 'Documentos de movimentações'
        self.context = {'titulo': self.title_name}

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        dados = models.DocMovStq.objects
        if self.context['data']:
            dados = dados.filter(data=self.context['data'])
        if self.context['descricao_usuario']:
            for chunk in self.context['descricao_usuario'].split():
                dados = dados.filter(
                    Q(descricao__icontains=chunk) |
                    Q(usuario__username__icontains=chunk)
                    )

        fields = ['num_doc', 'descricao', 'data', 'usuario__username']
        dados = dados.order_by('-num_doc').values(*fields)

        for row in dados:
            row['num_doc|LINK'] = reverse(
                'estoque:lista_movs__get', args=[row['num_doc']])

        headers = ['Documento', 'Descrição', 'Data', 'Usuário']
        self.context.update({
            'headers': headers,
            'fields': fields,
            'dados': dados,
            })

    def get(self, request, *args, **kwargs):
        self.context['form'] = self.Form_class()
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.request = request
        self.context['form'] = self.Form_class(request.POST)
        if self.context['form'].is_valid():
            self.cleanned_fields_to_context()
            self.mount_context()
            self.context_to_form_post()
            self.context['form'] = self.Form_class(self.context)
        return render(request, self.template_name, self.context)
