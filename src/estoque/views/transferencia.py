from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.views import View

from fo2.connections import db_cursor_so

from utils.functions.views import Fo2ViewMethods

from estoque import classes, forms, models


class Transferencia(PermissionRequiredMixin, View, Fo2ViewMethods):

    def __init__(self):
        super().__init__()
        self.Form_class = forms.TransferenciaForm
        self.template_name = 'estoque/transferencia.html'
        self.title_name = 'Movimentações'
        self.permission_required = 'estoque.can_transferencia'
        self.context = {'titulo': self.title_name}

    def valid_tipo(self):
        try:
            tip_mov = models.TipoMovStq.objects.get(codigo=self.kwargs['tipo'])
        except models.TipoMovStq.DoesNotExist as e:
            self.context.update({
                'erro_input': True,
                'erro_msg':
                    f'Tipo de movimento de estoque "{self.kwargs["tipo"]}" '
                    'não cadastrado.',
            })
            return
        return tip_mov

    def get_tipo(self):
        self.tip_mov = self.valid_tipo()
        if self.tip_mov:
            self.context.update({
                'tipo': self.tip_mov.codigo,
                'titulo': self.tip_mov.descricao,
            })

    def mount_context(self):
        try:
            transf = classes.Transfere(
                self.cursor, self.request, self.tip_mov,
                *(self.context[f] for f in [
                    'nivel', 'ref', 'tam',
                    'cores' if self.context['cores'] else 'cor',
                    'qtd', 'deposito_origem', 'deposito_destino',
                    'nova_ref', 'novo_tam',
                    'novas_cores' if self.context['novas_cores'] else 'nova_cor',
                    'num_doc', 'descricao']),
            )
        except Exception as e:
            self.context.update({
                'erro_input': True,
                'erro_msg': e,
            })
            return

        self.context.update({
            'mov_origem': self.tip_mov.trans_saida != 0,
            'mov_destino': self.tip_mov.trans_entrada != 0,
            'itens_saida': transf.itens_saida,
            'itens_entrada': transf.itens_entrada,
            'num_doc': transf.num_doc,
        })

        if 'executa' in self.request.POST:
            try:
                transf.exec()
            except Exception as e:
                self.context.update({
                    'erro_exec': True,
                    'erro_msg': e,
                })
                return
            self.context.update({
                'sucesso_msg': f"{self.context['titulo']} executada."
            })

    def get(self, request, *args, **kwargs):
        self.request = request
        self.cursor = db_cursor_so(request)
        self.get_tipo()
        if not self.tip_mov:
            return render(request, self.template_name, self.context)
        self.context['form'] = self.Form_class(
            cursor=self.cursor, user=request.user, tipo_mov=self.tip_mov)
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.request = request
        self.cursor = db_cursor_so(request)
        self.get_tipo()
        self.context['form'] = self.Form_class(
            request.POST, cursor=self.cursor, user=self.request.user, tipo_mov=self.tip_mov)
        if self.context['form'].is_valid():
            self.cleanned_fields_to_context()
            if self.tip_mov:
                self.mount_context()
            self.context['form'] = self.Form_class(
                self.context, cursor=self.cursor, user=self.request.user, tipo_mov=self.tip_mov)
        else:
            self.context.update({
                'erro_input': True,
                'erro_msg':
                    'Erro no preenchimento dos campos.',
            })
        return render(request, self.template_name, self.context)
