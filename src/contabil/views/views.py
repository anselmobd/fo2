from django.shortcuts import render

from geral.functions import get_empresa


def index(request):
    if get_empresa(request) == 'agator':
        return render(request, 'contabil/index_agator.html')
    else:
        return render(request, 'contabil/index.html')
