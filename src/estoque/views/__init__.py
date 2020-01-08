from django.shortcuts import render

from .estoque_na_data import *
from .executa_ajuste import *
from .edita_estoque import *
from .mostra_estoque import *
from .posicao_estoque import *
from .referencia_deposito import *
from .refs_com_movimento import *
from .valor_mp import *


def index(request):
    return render(request, 'estoque/index.html')
