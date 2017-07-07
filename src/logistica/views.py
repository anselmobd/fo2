from django.shortcuts import render
from django.views import View

from fo2.models import rows_to_dict_list
import logistica.models as models


def index(request):
    context = {}
    return render(request, 'logistica/index.html', context)


class DataSaida(View):
    template_name = 'logistica/data_saida.html'
    titulo = 'Controle de data de saída de NF'

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.titulo}
        sync_nf()
        return render(request, self.template_name, context)
