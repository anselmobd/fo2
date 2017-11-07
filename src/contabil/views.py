from django.shortcuts import render
from django.db import connections
from django.views import View

from .forms import InfAdProdForm
import contabil.models as models


def index(request):
    context = {}
    return render(request, 'contabil/index.html', context)


class InfAdProd(View):
    Form_class = InfAdProdForm
    template_name = 'contabil/infadprod.html'
    context = {
        'titulo': 'InfAdProd, EAN e Narrativa',
    }

    def get(self, request, *args, **kwargs):
        form = self.Form_class()
        context = self.context
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.Form_class(request.POST)
        context = self.context
        if form.is_valid():
            pedido = form.cleaned_data['pedido']

            cursor = connections['so'].cursor()
            data = models.infadprod_pro_pedido(cursor, pedido)
            from pprint import pprint
            pprint(data)
            if len(data) == 0:
                context['erro'] = '.'
            else:
                row = data[0]
                context.update({
                    'pedido': pedido,
                    'cliente': row['CLIENTE'],
                    'headers': ('Nível', 'Ref.', 'Cor', 'Tam.', 'Quantidade',
                                'infAdProd', 'EAN', 'Narrativa'),
                    'fields': ('NIVEL', 'REF', 'COR', 'TAM', 'QTD',
                               'INFADPROD', 'EAN', 'NARRATIVA'),
                    'data': data,
                })
        context['form'] = form
        return render(request, self.template_name, context)
