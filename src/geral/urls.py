from django.urls import re_path

import geral.views as views
from geral.views import configuracao
from geral.views import pop


app_name = 'geral'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    re_path(r'^painel/(?P<painel>[^/]*)/?$',
        views.PainelView.as_view(), name='painel'),

    re_path(r'^informativo/(?P<modulo>[^/]+)/(?P<id>[^/]+)?/?$',
        views.InformativoView.as_view(), name='informativo_modulo'),

    re_path(r'^resposavel_informativo/(?P<empresa>[^/]*)/$',
        views.informativo.ResponsavelInformativoView.as_view(), name='resposavel_informativo'),

    re_path(r'^pop/(?P<pop_assunto>[^/]+)/(?P<id>\d+)?$', pop.pop, name='pop'),

    re_path(r'^exec_gera_fluxo/$',
        views.ExecGeraFluxo.as_view(), name='exec_gera_fluxo'),

    re_path(r'^gera_fluxo/(?P<destino>.)/(?P<id>.+)/$',
        views.gera_fluxo, name='gera_fluxo'),

    re_path(r'^roteiros_de_fluxo/(?P<id>.+)/$',
        views.roteiros_de_fluxo, name='roteiros_de_fluxo'),

    re_path(r'^configuracao/$', configuracao.Configuracao.as_view(), name='configuracao'),

]
