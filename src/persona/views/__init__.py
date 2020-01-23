from django.shortcuts import render

from .aniversariantes import *
from .cria_usuario import *


def index(request):
    return render(request, 'persona/index.html')
