from pprint import pprint

from django.shortcuts import render


def index(request):
    return render(request, 'cd/index.html')


def teste_som(request):
    context = {}
    return render(request, 'cd/teste_som.html', context)
