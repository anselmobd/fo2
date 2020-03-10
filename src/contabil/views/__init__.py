from django.shortcuts import render

from .nota_fiscal import *
from .infadprod import *
from .remeindu import *
from .remeindunf import *


def index(request):
    return render(request, 'contabil/index.html')
