from django.shortcuts import render

from .aniversariantes import *


def index(request):
    return render(request, 'persona/index.html')
