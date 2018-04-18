from pprint import pprint

from django.shortcuts import render
from django.db import connections
from django.views import View

from fo2.models import rows_to_dict_list_lower

import lotes.models

from cd.forms import LoteForm


def index(request):
    context = {}
    return render(request, 'cd/index.html', context)


class LotelLocal(View):
    Form_class = LoteForm
    template_name = 'cd/lote_local.html'
    title_name = 'Bipa lote indicando local'

    def mount_context(self, cursor, form):
        endereco = form.cleaned_data['endereco']
        lote = form.cleaned_data['lote']
        identificado = form.cleaned_data['identificado']

        context = {'endereco': endereco}

        try:
            lote_rec = lotes.models.Lote.objects.get(lote=lote)
        except lotes.models.Lote.DoesNotExist:
            context.update({'erro': 'Lote não encontrado'})
            return context
        context.update({
            'op': lote_rec.op,
            'referencia': lote_rec.referencia,
            'cor': lote_rec.cor,
            'tamanho': lote_rec.tamanho,
            'qtd_produzir': lote_rec.qtd_produzir,
            'local': lote_rec.local,
            })

        # print('identificado={}'.format(identificado))
        if identificado:
            # print('if identificado')
            form.data['identificado'] = None
            form.data['lote'] = None
            if lote != identificado:
                context.update({
                    'erro': 'A confirmação é bipando o mesmo lote. '
                            'Identifique o lote novamente.'})
                return context

            try:
                lote_rec = lotes.models.Lote.objects.get(lote=lote)
            except lotes.models.Lote.DoesNotExist:
                context.update({
                    'erro': 'Lote não encontrado no banco de dados'})
                return context

            lote_rec.local = endereco
            lote_rec.save()

            context['identificado'] = identificado
        else:
            # print('if not identificado')
            context['lote'] = lote
            # periodo = lote[:4]
            # ordem_confeccao = lote[-5:]

            # data = lotes.models.posicao_get_op(
            #     cursor, periodo, ordem_confeccao)
            # if len(data) == 0:
            #     context.update({'erro': 'Lote não encontrado'})
            #     return context
            # row = data[0]
            # op = row['OP']

            # print('lote_rec.local = "{}" endereco = "{}"'.format(
            #     lote_rec.local, endereco))
            if lote_rec.local != endereco:
                context['confirma'] = True
                form.data['identificado'] = form.data['lote']
            form.data['lote'] = None

        # lotes_rec = lotes.models.Lote.objects.get(local=endereco)
        # data = rows_to_dict_list_lower(lotes_rec)
        # pprint(data)

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
            # pprint(request.POST)
            cursor = connections['so'].cursor()
            data = self.mount_context(cursor, form)
            context.update(data)
        context['form'] = form
        return render(request, self.template_name, context)
