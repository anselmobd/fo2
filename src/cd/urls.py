from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^s/$', views.teste_som, name='teste_som'),

    url(r'^lote_local/$', views.LotelLocal.as_view(), name='lote_local'),

    url(r'^estoque/(?P<ordem>.)/(?P<filtro>.+)/$',
        views.Estoque.as_view(), name='estoque_filtro'),
    url(r'^estoque/$', views.Estoque.as_view(), name='estoque'),

    url(r'^troca_local/$', views.TrocaLocal.as_view(), name='troca_local'),

    url(r'^inconsist/(?P<ordem>.-?)/(?P<opini>-?\d+)/$',
        views.Inconsistencias.as_view(), name='inconsist_opini'),
    url(r'^inconsist/$', views.Inconsistencias.as_view(), name='inconsist'),

    url(r'^inconsist_detalhe/(?P<op>\d+)/$',
        views.InconsistenciasDetalhe.as_view(),
        name='inconsist_detalhe_op'),

    url(r'^visao_cd/$',
        views.VisaoCd.as_view(), name='visao_cd'),

    url(r'^visao_rua/(?P<rua>[^/]+)/$',
        views.VisaoRua.as_view(), name='visao_rua__get'),

    url(r'^visao_rua_detalhe/(?P<rua>[^/]+)/$',
        views.VisaoRuaDetalhe.as_view(), name='visao_rua_detalhe__get'),

    url(r'^solicitacoes/(?P<id>[^/]+)?$',
        views.Solicitacoes.as_view(), name='solicitacoes'),

    url(r'^solicitacao_detalhe/(?P<solicit_id>[^/]+)'
        '/(?P<acao>[^/]+)/(?P<id>[^/]+)$',
        views.SolicitacaoDetalhe.as_view(),
        name='solicitacao_detalhe__get3'),
    url(r'^solicitacao_detalhe/(?P<solicit_id>[^/]+)'
        '/(?P<acao>[^/]+)$',
        views.SolicitacaoDetalhe.as_view(),
        name='solicitacao_detalhe__get2'),
    url(r'^solicitacao_detalhe/(?P<solicit_id>[^/]+)',
        views.SolicitacaoDetalhe.as_view(), name='solicitacao_detalhe'),

    url(r'^solicita/(?P<solicitacao_id>[^/]+)/'
        '(?P<lote>[^/]+)/(?P<qtd>[^/]+)/$',
        views.solicita_lote, name='solicita_lote'),

    url(r'^mapa/$', views.Mapa.as_view(), name='mapa'),

    url(r'^endereco_lote/(?P<lote>[^/]+)?$', views.EnderecoLote.as_view(),
        name='endereco_lote'),

    url(r'^grade_estoque/(?P<referencia>[^/]+)/(?P<detalhe>[^/]+)?/?$',
        views.Grade.as_view(), name='grade_estoque_detalhe'),
    url(r'^grade_estoque/(?P<referencia>[^/]+)?/?$',
        views.Grade.as_view(), name='grade_estoque'),

    url(r'^historico/?$',
        views.Historico.as_view(), name='historico'),

    url(r'^historico/(?P<op>[^/]+)?$',
        views.Historico.as_view(), name='historico__get'),

    url(r'^historico_lote/(?P<lote>[^/]+)?$',
        views.HistoricoLote.as_view(), name='historico_lote'),
]
