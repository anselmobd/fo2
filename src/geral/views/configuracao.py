from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.views import View

import geral.forms as forms
from geral.functions import (
    config_get_value,
    config_set_value,
)


class Configuracao(PermissionRequiredMixin, View):
    def __init__(self, *args, **kwargs):
        self.permission_required = 'geral.change_config'
        self.Form_class = forms.ConfigForm
        self.template_name = 'geral/config.html'
        self.title_name = 'Configuração'

    def get_values(self, request):
        values = {}
        for field in self.Form_class.field_param:
            param = self.Form_class.field_param[field]
            if request.user.is_superuser:
                values[field] = config_get_value(param)
            else:
                values[field] = config_get_value(param, request.user)
        return values

    def set_values(self, request, values):
        if request.user.is_superuser:
            usuario = None
        else:
            usuario = request.user
        ok = True
        for field in self.Form_class.field_param:
            param = self.Form_class.field_param[field]
            ok = ok and config_set_value(param, values[field], usuario=usuario)
        return ok

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        values = self.get_values(request)
        form.fields["op_unidade"].initial = values['op_unidade']
        form.fields["dias_alem_lead"].initial = values['dias_alem_lead']
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            values = {}
            values['op_unidade'] = form.cleaned_data['op_unidade']
            values['dias_alem_lead'] = form.cleaned_data['dias_alem_lead']
            if self.set_values(request, values):
                context['msg'] = 'Valores salvos!'
            else:
                context['msg'] = 'Houve algum erro ao salvar os valores!'
        context['form'] = form
        return render(request, self.template_name, context)
