from pprint import pprint

from django.shortcuts import render


def index(request):
    return render(request, 'servico/index.html')
