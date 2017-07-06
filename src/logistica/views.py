from pprint import pprint

from django.shortcuts import render
from django.views import View
from django.db import connections

from fo2.models import rows_to_dict_list, cursorF1
import logistica.models as models


def index(request):
    context = {}
    return render(request, 'logistica/index.html', context)


def sync_nf():
    cursor = connections['so'].cursor()
    sql = '''
        SELECT
          f.NUM_NOTA_FISCAL NF
        FROM FATU_050 f
        ORDER BY
          f.NUM_NOTA_FISCAL
    '''
    cursor.execute(sql)
    nfs_st = rows_to_dict_list(cursor)
    # pprint(datast)
    # nfs_st = [{'NF': 102}, {'NF': 103}, ]

    nfs = list(models.NotaFiscal.objects.values_list('numero'))

    for row in nfs_st:
        if (row['NF'],) not in nfs:
            print('insert {}'.format(row['NF']))
            nf = models.NotaFiscal(numero=row['NF'])
            nf.save()

    pprint(nfs)


class DataSaida(View):
    template_name = 'logistica/data_saida.html'
    titulo = 'Controle de data de saída de NF'

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.titulo}
        sync_nf()
        return render(request, self.template_name, context)
