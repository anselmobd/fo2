from django.urls import re_path

from . import views


app_name = 'geral'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    re_path(r'^deposito/$', views.deposito, name='deposito'),

    re_path(r'^estagio/$', views.estagio, name='estagio'),

    re_path(r'^periodo_confeccao/$',
        views.periodo_confeccao, name='periodo_confeccao'),

    re_path(r'^painel/(?P<painel>[^/]*)/?$',
        views.PainelView.as_view(), name='painel'),

    re_path(r'^informativo/(?P<modulo>[^/]+)/(?P<id>[^/]+)?/?$',
        views.InformativoView.as_view(), name='informativo_modulo'),

    re_path(r'^pop/(?P<pop_assunto>[^/]+)/(?P<id>\d+)?$', views.pop, name='pop'),

    re_path(r'^gera_fluxo_dot/$',
        views.GeraFluxoDot.as_view(), name='gera_fluxo_dot'),

    re_path(r'^fluxo/(?P<destino>.)/(?P<id>.+)/$',
        views.gera_fluxo_dot, name='fluxo'),

    re_path(r'^roteiros_de_fluxo/(?P<id>.+)/$',
        views.roteiros_de_fluxo, name='roteiros_de_fluxo'),

    re_path(r'^unidade/$', views.unidade, name='unidade'),

    re_path(r'^configuracao/$', views.Configuracao.as_view(), name='configuracao'),

]
