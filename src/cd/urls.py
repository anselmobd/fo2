from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='cd_index'),
    url(r'^s/$', views.teste_som, name='teste_som'),
    url(r'^lote_local/$', views.LotelLocal.as_view(), name='cd_lote_local'),
    url(r'^estoque/$', views.Estoque.as_view(), name='cd_estoque'),
    url(r'^estoque/(?P<ordem>.)/(?P<filtro>.+)/$',
        views.Estoque.as_view(), name='cd_estoque_filtro'),
    url(r'^troca_local/$', views.TrocaLocal.as_view(), name='cd_troca_local'),
    url(r'^inconsist/$', views.Inconsistencias.as_view(), name='cd_inconsist'),
    url(r'^inconsist/(?P<ordem>.-?)/(?P<opini>-?\d+)/$',
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
    url(r'^solicitacao_detalhe/(?P<solicit_id>[^/]+)'
        '(/(?P<acao>[^/]+))?(/(?P<id>[^/]+))?$',
        views.SolicitacaoDetalhe.as_view(), name='cd_solicitacao_detalhe'),
    url(r'^solicita/(?P<solicitacao_id>[^/]+)/'
        '(?P<lote>[^/]+)/(?P<qtd>[^/]+)/$',
        views.solicita_lote, name='cd_solicita_lote'),
    url(r'^mapa/$', views.Mapa.as_view(), name='cd_mapa'),
    url(r'^endereco_lote/(?P<lote>[^/]+)?$', views.EnderecoLote.as_view(),
        name='cd_endereco_lote'),
    url(r'^grade_estoque/(?P<referencia>[^/]+)?/?$',
        views.Grade.as_view(), name='cd_grade_estoque'),
    url(r'^grade_estoque/(?P<referencia>[^/]+)/(?P<detalhe>[^/]+)?/?$',
        views.Grade.as_view(), name='cd_grade_estoque_detalhe'),
    url(r'^historico/?$',
        views.Historico.as_view(), name='cd_historico'),
    url(r'^historico_lote/(?P<lote>[^/]+)?$',
        views.HistoricoLote.as_view(), name='cd_historico_lote'),
]
