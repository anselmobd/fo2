from django.shortcuts import render
from django.views import View

from fo2.models import rows_to_dict_list
import logistica.models as models


def index(request):
    context = {}
    return render(request, 'logistica/index.html', context)
