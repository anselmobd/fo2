from pprint import pprint

from django.utils import timezone
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Q

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.functions import untuple_keys_concat
from geral.functions import get_empresa

from logistica.models import *
from logistica.queries import get_chave_pela_nf
from logistica.forms import *


def index(request):
    if get_empresa(request) == 'agator':
        return render(request, 'logistica/index_agator.html')
    else:
        return render(request, 'logistica/index.html')


def notafiscal_nf(request, *args, **kwargs):
    if 'nf' not in kwargs or kwargs['nf'] is None:
        return redirect('logistica:index')

    cursor = db_cursor_so(request)
    data_nf = get_chave_pela_nf(cursor, kwargs['nf'])
    if len(data_nf) == 0:
        return redirect('logistica:index')

    return redirect(
        'logistica:notafiscal_chave', data_nf[0]['NUMERO_DANF_NFE'])
