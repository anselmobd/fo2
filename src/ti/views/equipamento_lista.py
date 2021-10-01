from pprint import pprint

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse

from base.views import O2BaseGetPostView

from utils.forms import FiltroForm
import ti.forms
import ti.models


class EquipamentoLista(O2BaseGetPostView):
    pass