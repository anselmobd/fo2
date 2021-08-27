from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
from django_tables2 import RequestConfig

from fo2.connections import db_cursor_so

from utils.functions.models import rows_to_dict_list
from geral.functions import get_empresa

import lotes.models as models
import lotes.forms as forms
from lotes.tables import ImpressoraTermicaTable


def index(request):
    if get_empresa(request) == 'agator':
        return render(request, 'lotes/index_agator.html')
    else:
        return render(request, 'lotes/index.html')


def impressoraTermica(request):
    table = ImpressoraTermicaTable(
        models.ImpressoraTermica.objects.all())
    RequestConfig(request, paginate=False).configure(
        table)
    return render(
        request, 'lotes/impressora_termica.html',
        {'impressora_termica': table,
         'titulo': 'Impressora Térmica',
         })
