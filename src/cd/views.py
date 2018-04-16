from django.shortcuts import render
from django.db import connections
from django.views import View

from cd.forms import LoteForm

import lotes.models


def index(request):
    context = {}
    return render(request, 'cd/index.html', context)


class LotelLocal(View):
    Form_class = LoteForm
    template_name = 'cd/lote_local.html'
    title_name = 'Bipa lote indicando local'

    def mount_context(self, cursor, lote):
        context = {'lote': lote}
        periodo = lote[:4]
        ordem_confeccao = lote[-5:]

        data = lotes.models.posicao_get_op(
            cursor, periodo, ordem_confeccao)
        if len(data) == 0:
            context.update({'erro': 'Lote não encontrado'})
            return context

        row = data[0]
        op = row['OP']
        context.update({'op': op})

        return context

    def get(self, request, *args, **kwargs):
        if 'lote' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'lote' in kwargs:
            form.data['lote'] = kwargs['lote']
        if form.is_valid():
            lote = form.cleaned_data['lote']
            cursor = connections['so'].cursor()
            data = self.mount_context(cursor, lote)
            context.update(data)
        context['form'] = form
        return render(request, self.template_name, context)
