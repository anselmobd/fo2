from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='cd'),
    url(r'^lote_local/$', views.LotelLocal.as_view(), name='cd_lote_local'),
    url(r'^estoque/$', views.Estoque.as_view(), name='cd_estoque'),
    url(r'^estoque/(?P<ordem>.)/(?P<filtro>.+)/$',
        views.Estoque.as_view(), name='cd_estoque_filtro'),
    url(r'^troca_local/$', views.TrocaLocal.as_view(), name='cd_troca_local'),
    url(r'^inconsist/$', views.Inconsistencias.as_view(), name='cd_inconsist'),
    url(r'^inconsist/(?P<ordem>.-?)/(?P<opini>\d+)/$',
        views.Inconsistencias.as_view(), name='cd_inconsist_opini'),
    url(r'^inconsist_detalhe/(?P<op>\d+)/$',
        views.InconsistenciasDetalhe.as_view(),
        name='cd_inconsist_detalhe_op'),
    url(r'^conferencia/$',
        views.ConferenciaSimples.as_view(), name='cd_conferencia'),
    url(r'^conferencia_detalhada/$',
        views.Conferencia.as_view(), name='cd_conferencia_detalhada'),
    url(r'^solicitacoes/(?P<id>[^/]+)?$',
        views.Solicitacoes.as_view(), name='cd_solicitacoes'),
    url(r'^solicitacao_detalhe/(?P<solicit_id>[^/]+)?$',
        views.SolicitacaoDetalhe.as_view(), name='cd_solicitacao_detalhe'),
    url(r'^solicita/(?P<solicitacao_id>[^/]+)/'
        '(?P<lote>[^/]+)/(?P<qtd>[^/]+)?/$',
        views.solicita_lote, name='cd_solicita_lote'),
    url(r'^mapa/$', views.Mapa.as_view(), name='cd_mapa'),
]
