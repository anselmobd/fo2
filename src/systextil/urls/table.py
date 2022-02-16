from django.urls import re_path
from systextil.views import apoio_index

from systextil.views.table import (
    deposito,
    colecao,
    estagio,
    periodo_confeccao,
    unidade,
)


urlpatterns = [

    re_path(r'^colecao/$', colecao.view, name='colecao'),

    re_path(r'^deposito/$', deposito.deposito, name='deposito'),

    re_path(r'^estagio/$', estagio.view, name='estagio'),

    re_path(r'^periodo_confeccao/$', periodo_confeccao.view, name='periodo_confeccao'),

    re_path(r'^unidade/$', unidade.view, name='unidade'),

]
