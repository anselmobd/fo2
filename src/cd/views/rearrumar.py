from pprint import pprint

from django.db import connections
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.views import View

import lotes.models

import cd.forms


class Rearrumar(PermissionRequiredMixin, View):

    def __init__(self):
        self.permission_required = 'lotes.can_inventorize_lote'
        self.Form_class = cd.forms.RearrumarForm
        self.template_name = 'cd/rearrumar.html'
        self.title_name = 'Rearrumar palete'

    def mount_context(self, request, form):
        cursor = connections['so'].cursor()

        local = form.cleaned_data['local']
        rua = form.cleaned_data['rua']

        context = {
            'local': local,
            'rua': rua,
        }

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            data = self.mount_context(request, form)
            context.update(data)
        context['form'] = form
        return render(request, self.template_name, context)
