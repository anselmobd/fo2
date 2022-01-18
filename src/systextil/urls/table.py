from django.urls import re_path
from systextil.views import apoio_index

from systextil.views.table import (
    deposito,
    colecao,
)


urlpatterns = [

    re_path(r'^deposito/$', deposito.deposito, name='deposito'),

    re_path(r'^colecao/$', colecao.view, name='colecao'),

]
