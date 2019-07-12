from django.views import View
from django.shortcuts import render


def index(request):
    context = {}
    return render(request, 'manutencao/index.html', context)


class Rotinas(View):
    pass
