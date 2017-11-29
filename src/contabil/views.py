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
    title_name = 'Itens de pedido (InfAdProd, EAN e Narrativa)'

    def get(self, request):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.Form_class(request.POST)
        context = {'titulo': self.title_name}
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
