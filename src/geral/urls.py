from django.conf.urls import url

from . import views


app_name = 'geral'
urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^deposito/$', views.deposito, name='deposito'),

    url(r'^estagio/$', views.estagio, name='estagio'),

    url(r'^periodo_confeccao/$',
        views.periodo_confeccao, name='periodo_confeccao'),

    url(r'^painel/(?P<painel>[^/]*)/?$',
        views.PainelView.as_view(), name='painel'),

    url(r'^informativo/(?P<modulo>[^/]+)/(?P<id>[^/]+)?/?$',
        views.InformativoView.as_view(), name='informativo_modulo'),

    url(r'^pop/(?P<pop_assunto>[^/]+)/(?P<id>\d+)?$', views.pop, name='pop'),

    url(r'^gera_fluxo_dot/$',
        views.GeraFluxoDot.as_view(), name='gera_fluxo_dot'),

    url(r'^fluxo/(?P<destino>.)/(?P<id>.+)/$',
        views.gera_fluxo_dot, name='fluxo'),

    url(r'^roteiros_de_fluxo/(?P<id>.+)/$',
        views.roteiros_de_fluxo, name='roteiros_de_fluxo'),

    url(r'^unidade/$', views.unidade, name='unidade'),

    url(r'^configuracao/$', views.Configuracao.as_view(), name='configuracao'),

]
