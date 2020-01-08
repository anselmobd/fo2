import datetime
import time
import re
import hashlib
from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.views import View
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.shortcuts import redirect
from django.core.exceptions import SuspiciousOperation

from utils.views import (
    totalize_data, totalize_grouped_data, TableHfs, request_hash_trail)
from fo2.template import group_rowspan
from geral.functions import request_user, has_permission
import produto.queries

from estoque import forms
from estoque import models
from estoque import queries
from estoque.classes import TransacoesDeAjuste
from estoque.functions import transfo2_num_doc, transfo2_num_doc_dt

from .executa_ajuste import *
from .edita_estoque import *
from .mostra_estoque import *
from .posicao_estoque import *
from .referencia_deposito import *
from .refs_com_movimento import *
from .valor_mp import *


def index(request):
    return render(request, 'estoque/index.html')


class EstoqueNaData(View):
    pass
