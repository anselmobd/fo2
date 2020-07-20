from pprint import pprint

from django.shortcuts import redirect, render


def index(request):
    return render(request, 'cd/index.html')


def teste_som(request):
    return render(request, 'cd/teste_som.html')


def movimentacao(request):
    return render(request, 'cd/movimentacao.html')


def menu_desligado(request):
    return redirect('apoio_ao_erp')
