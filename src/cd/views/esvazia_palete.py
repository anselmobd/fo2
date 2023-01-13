from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from fo2.connections import db_cursor_so

from base.models import Colaborador
from systextil.models import Usuario as SystextilUsuario

import cd.forms
import cd.views.gerais
from cd.queries.endereco import (
    conteudo_local,
    esvazia_palete,
    get_palete,
    palete_guarda_hist,
)


class EsvaziaPalete(LoginRequiredMixin, View):

    def __init__(self):
        self.Form_class = cd.forms.EsvaziaPaleteForm
        self.template_name = 'cd/esvazia_palete.html'
        self.context = {'titulo': 'Esvazia palete'}

    def mount_context(self):
        try:
            colab = Colaborador.objects.get(user=self.request.user)
        except Colaborador.DoesNotExist as e:
            self.context.update({
                'erro': 'Não é possível utilizar um usuário que não '
                    'está cadastrado como colaborador.'
            })
            return

        try:
            s_user = SystextilUsuario.objects.get(codigo_usuario=colab.matricula)
        except SystextilUsuario.DoesNotExist as e:
            self.context.update({
                'erro': 'Não é possível utilizar um colaborador sem '
                    'matrícula válida ou inativo.'
            })
            return

        cursor = db_cursor_so(self.request)

        identificado = self.context['form'].cleaned_data['identificado']
        palete = self.context['form'].cleaned_data['palete'].upper()
        self.context.update({
            'palete': palete,
            'identificado': identificado,
        })

        dados_palete = get_palete(cursor, palete)
        if not dados_palete:
            self.context.update({
                'erro': "Palete inexistênte."})
            self.context['identificado'] = None
            return

        lotes_end = conteudo_local(cursor, local=palete)
        if lotes_end:
            self.context.update({
                'quant_lotes': len(lotes_end),
            })
        else:
            self.context.update({
                'erro': "Palete já vazio."})
            self.context['identificado'] = None
            return

        if not identificado:
            self.context['identificado'] = palete
            self.context['form'].data = self.context['form'].data.copy()
            self.context['form'].data['identificado'] = palete
            self.context['form'].data['palete'] = None
            return

        if identificado != palete:
            self.context.update({
                'erro': "Não confirmado mesmo palete."})
            self.context['identificado'] = None
            return

        if not palete_guarda_hist(cursor, palete, s_user.usuario):
            self.context.update({
                'erro': f"Erro ao guardar histórico do palete {palete}."})

        if esvazia_palete(cursor, palete):
            self.context.update({
                'mensagem': f"{palete} esvaziado!"})
        else:
            self.context.update({
                'erro': f"Erro ao esvaziar palete {palete}."})

        self.context['identificado'] = None


    def get(self, request, *args, **kwargs):
        self.context['form'] = self.Form_class()
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        request = self.request
        self.context['form'] = self.Form_class(request.POST)
        if self.context['form'].is_valid():
            self.mount_context()
        return render(request, self.template_name, self.context)
