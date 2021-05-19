from pprint import pprint

from django.db import IntegrityError
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from geral.functions import has_permission

import systextil.models
from comercial.views.estoque import grade_meta_estoque

import lotes.forms as forms
import lotes.models as models
from lotes.models.functions.meta import calculaMetaGiroTodas


class LeadColecao(View):

    def __init__(self):
        self.Form_class = forms.LeadColecaoForm
        self.template_name = 'lotes/lead_colecao.html'
        self.title_name = 'Lead por coleção'
        self.id = None
        self.context = {'titulo': self.title_name}

    def lista(self):
        try:
            colecoes = systextil.models.Colecao.objects.exclude(
                colecao=0).order_by('colecao')
        except systextil.models.Colecao.DoesNotExist:
            self.context.update({
                'msg_erro': 'Coleções não encontradas',
            })
            return

        try:
            LC = models.RegraColecao.objects.all().order_by('colecao')
        except models.RegraColecao.DoesNotExist:
            self.context.update({
                'msg_erro': 'Parâmetros de coleções não encontrados',
            })
            return

        lcs = {}
        inter_col = colecoes.iterator()
        inter_LC = LC.iterator()
        walk = 'b'   # from, to, both
        while True:
            if walk in ['f', 'b']:
                try:
                    col = next(inter_col)
                except StopIteration:
                    col = None

            if walk in ['t', 'b']:
                try:
                    lc = next(inter_LC)
                except StopIteration:
                    lc = None

            if lc is None and col is None:
                break

            rec = {
                'descr_colecao': '',
                'lead': 0,
            }
            acao_definida = False

            if lc is not None:
                if col is None or col.colecao > lc.colecao:
                    acao_definida = True
                    rec['status'] = 'd'
                    rec['colecao'] = lc.colecao
                    walk = 't'

            if not acao_definida:
                rec['colecao'] = col.colecao
                rec['descr_colecao'] = col.descr_colecao
                if lc is None or col.colecao < lc.colecao:
                    acao_definida = True
                    rec['status'] = 'i'
                    walk = 'f'

            if not acao_definida:
                rec['lead'] = lc.lead
                rec['status'] = 'u'
                walk = 'b'

            lcs[rec['colecao']] = rec

        data = []
        for key in lcs:
            if lcs[key]['status'] == 'd':
                try:
                    models.RegraColecao.objects.filter(colecao=key).delete()
                except models.RegraColecao.DoesNotExist:
                    self.context.update({
                        'msg_erro': 'Erro apagando parâmetros de coleção',
                    })
                    return
                continue

            if lcs[key]['status'] == 'i':
                try:
                    lc = models.RegraColecao()
                    lc.colecao = key
                    lc.lead = 0
                    lc.save()
                except Exception:
                    self.context.update({
                        'msg_erro': 'Erro salvando lead',
                    })
                    return
            lcs[key].update({
                'edit': ('<a title="Editar" '
                         'href="{}">'
                         '<span class="glyphicon glyphicon-pencil" '
                         'aria-hidden="true"></span></a>'
                         ).format(reverse(
                            'producao:lead_colecao', args=[key])),
            })
            data.append(lcs[key])

        headers = ['Coleção', 'Descrição', 'Lead (dias)']
        fields = ['colecao', 'descr_colecao', 'lead']
        if has_permission(self.request, 'lotes.change_leadcolecao'):
            headers.insert(0, '')
            fields.insert(0, 'edit')
        self.context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
            'safe': ['edit'],
        })

    def get(self, request, *args, **kwargs):
        self.request = request

        if 'id' in kwargs:
            self.id = kwargs['id']

        if self.id:
            if has_permission(request, 'lotes.change_leadcolecao'):
                try:
                    lc = models.RegraColecao.objects.get(colecao=self.id)
                except models.RegraColecao.DoesNotExist:
                    self.context.update({
                        'msg_erro': 'Parâmetros de coleção não encontrados',
                    })
                    return render(
                        self.request, self.template_name, self.context)

                try:
                    colecao = systextil.models.Colecao.objects.get(
                        colecao=self.id)
                except systextil.models.Colecao.DoesNotExist:
                    self.context.update({
                        'msg_erro': 'Coleção não encontrada',
                    })
                    return render(
                        self.request, self.template_name, self.context)

                self.context['id'] = self.id
                self.context['descr_colecao'] = colecao.descr_colecao
                self.context['form'] = self.Form_class(
                    initial={'lead': lc.lead})
            else:
                self.id = None

        if not self.id:
            self.lista()

        return render(self.request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.request = request

        if 'id' in kwargs:
            self.id = kwargs['id']

        form = self.Form_class(request.POST)
        if self.id and form.is_valid():
            lead = form.cleaned_data['lead']

            try:
                lc = models.RegraColecao.objects.get(colecao=self.id)
            except models.RegraColecao.DoesNotExist:
                self.context.update({
                    'msg_erro': 'Parâmetros de coleção não encontrados',
                })
                return render(
                    self.request, self.template_name, self.context)

            try:
                lc.lead = lead
                lc.save()

                cursor = db_cursor_so(request)
                calculaMetaGiroTodas(cursor)

            except IntegrityError as e:
                self.context['msg_erro'] = 'Ocorreu um erro ao gravar ' \
                    'o lead. <{}>'.format(str(e))

            self.lista()
        else:
            self.context['form'] = form
        return render(self.request, self.template_name, self.context)
