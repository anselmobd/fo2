from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import connection
from django.db.models import F, Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from utils.classes import TermalPrint
from utils.functions.digits import *

import lotes.models

import cd.queries as queries
import cd.forms


class EtiquetasSolicitacoes(PermissionRequiredMixin, View):

    def __init__(self):
        self.permission_required = 'lotes.can_print__solicitacao_parciais'
        self.Form_class = cd.forms.EtiquetasSolicitacoesForm
        self.template_name = 'cd/etiq_solicitacoes.html'
        self.context = {
            'titulo': 'Etiquetas de solicitações',
            'passo': 1,
        }

    def imprime(self, data):
        try:
            impresso = lotes.models.Impresso.objects.get(
                slug='etiqueta-de-solicitacao')
        except lotes.models.Impresso.DoesNotExist:
            self.context.update({
                'msg': 'Impresso etiqueta-de-solicitacao não cadastrado',
            })
            return False

        try:
            usuario_impresso = lotes.models.UsuarioImpresso.objects.get(
                usuario=self.request.user, impresso=impresso)
        except lotes.models.UsuarioImpresso.DoesNotExist:
            self.context.update({
                'msg': 'Impresso não cadastrado para o usuário',
            })
            return False

        teg = TermalPrint(usuario_impresso.impressora_termica.nome)
        teg.template(usuario_impresso.modelo.gabarito, '\r\n')
        teg.printer_start()
        try:
            for row in data:
                teg.context(row)
                teg.printer_send()
        finally:
            teg.printer_end()

        return True

    def marca_impresso(self, solicitacao):
        try:
            solicitacao_prt = lotes.models.SolicitaLotePrinted(
                solicitacao=solicitacao,
                printed_by=self.request.user
            )
            solicitacao_prt.save()
            return True
        except Exception:
            return False

    def seleciona(self, data, selecao):
        intervals = [
            v.strip()
            for v in selecao.split(',')
            if v.strip() not in ('', '-')
        ]

        if len(intervals) == 0:
            return data

        selecionadas = set()
        for interval in intervals:
            limits = [i.strip() for i in interval.split('-')]
            ini = limits[0]
            try:
                fim = limits[1]
            except Exception:
                fim = ini
            ini = int(ini) if ini != '' else 1
            fim = int(fim) if fim != '' else len(data)
            for num in range(ini, fim+1):
                selecionadas.add(num)
        return [d for n, d in enumerate(data) if n+1 in selecionadas]

    def mount_context(self, form):
        cursor = connection.cursor()

        numero = form.cleaned_data['numero']
        buscado_numero = form.cleaned_data['buscado_numero']
        selecao = form.cleaned_data['selecao']

        self.context.update({
            'numero': numero,
        })

        solicitacao = lotes.models.SolicitaLote.objects.get(id=numero[:-2])

        self.context.update({
            'codigo': solicitacao.codigo,
            'nome': solicitacao.descricao,
        })

        data = lotes.models.SolicitaLoteQtd.objects.values(
            'lote__op', 'lote__lote', 'lote__qtd_produzir',
            'lote__referencia', 'lote__cor', 'lote__tamanho'
        ).annotate(
            lote_ordem=Coalesce('lote__local', Value('0000')),
            lote__local=Coalesce('lote__local', Value('-Ausente-')),
            qtdsum=Sum('qtd')
        ).filter(
            solicitacao=solicitacao,
        ).exclude(
            lote__qtd_produzir=F('qtdsum'),
        ).order_by(
            'lote_ordem', 'lote__op', 'lote__referencia', 'lote__cor',
            'lote__tamanho', 'lote__lote'
        )

        for n, row in enumerate(data):
            row['n'] = n + 1
            row['numero'] = numero
            row['lote__lote|LINK'] = reverse(
                'producao:posicao__get',
                args=[row['lote__lote']])
            row['lote__lote|TARGET'] = '_BLANK'

        self.context.update({
            'headers': [
                'Nº', 'Endereço', 'OP', 'Lote',
                'Referência', 'Cor', 'Tamanho',
                'Quant. original', 'Quant. Solicitada'
            ],
            'fields': [
                'n', 'lote__local', 'lote__op', 'lote__lote',
                'lote__referencia', 'lote__cor', 'lote__tamanho',
                'lote__qtd_produzir', 'qtdsum'
            ],
            'data': data,
        })

        if self.request.POST.get("volta_para_busca"):
            self.context.update({
                'passo': 1,
            })

        elif self.request.POST.get("volta_para_imprime"):
            self.context.update({
                'passo': 2,
            })

        elif self.request.POST.get("imprime"):
            if buscado_numero == numero:
                data_selecao = []
                try:
                    data_selecao = self.seleciona(data, selecao)
                except Exception as e:
                    self.context.update({
                        'msg': 'Seleção para impressão inválida',
                        'passo': 2,
                    })
                if data_selecao:
                    if self.imprime(data_selecao):
                        form.data['impresso_numero'] = numero
                        self.context.update({
                            'msg': 'Enviado para a impressora',
                            'passo': 3,
                        })
                    else:
                        self.context.update({
                            'passo': 2,
                        })
                else:
                    self.context.update({
                        'msg': 'Nada selecionado',
                        'passo': 2,
                    })
            else:
                form.data['numero'] = ''
                self.context.update({
                    'numero': None,
                    'passo': 1,
                })
                form.add_error(
                    'numero', "Número não pode ser alterado no passo 2"
                )

        elif self.request.POST.get("confirma"):
            if buscado_numero == numero:
                if self.marca_impresso(solicitacao):
                    form.data['numero'] = ''
                    self.context.update({
                        'msg': 'Impressão marcada como confirmada',
                        'passo': 1,
                    })
                else:
                    self.context.update({
                        'msg': 'Erro ao marcar impressão como confirmada',
                        'passo': 3,
                    })
            else:
                form.data['numero'] = ''
                self.context.update({
                    'numero': None,
                    'passo': 1,
                })
                form.add_error(
                    'numero', "Número não pode ser alterado no passo 3"
                )

        else:  # self.request.POST.get("busca"):
            form.data['buscado_numero'] = numero
            self.context.update({
                'passo': 2,
            })

    def get(self, request, *args, **kwargs):
        self.request = request
        form = self.Form_class()
        self.context['form'] = form
        return render(self.request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.request = request
        mutable_request_post = self.request.POST.copy()
        form = self.Form_class(mutable_request_post)
        if form.is_valid():
            self.mount_context(form)
        self.context['form'] = form
        return render(self.request, self.template_name, self.context)
