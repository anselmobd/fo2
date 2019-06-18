from pprint import pprint

from django.shortcuts import render
from django.db import connections
from django.views import View

from base.views import O2BaseGetPostView

import produto.queries

import comercial.forms as forms
import comercial.models as models


class EstoqueDesejado(O2BaseGetPostView):
    pass
