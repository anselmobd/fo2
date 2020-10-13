from django.conf.urls import url

import cd.views as views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^s/$', views.teste_som, name='teste_som'),

    url(r'^estoque/(?P<ordem>.)/(?P<filtro>.+)/$',
        views.Estoque.as_view(), name='estoque_filtro'),
    url(r'^estoque/$', views.Estoque.as_view(), name='estoque'),

    url(r'^troca_local/$', views.menu_desligado, name='troca_local'),
    url(r'^troca_local_/$', views.TrocaLocal.as_view(), name='troca_local_'),

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

    url(r'^ajax/libera_coleta_de_solicitacao/(?P<num>[^/]+)?$',
        views.libera_coleta_de_solicitacao,
        name='libera_coleta_de_solicitacao'),

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

    url(r'^endereco_lote/ajax/(?P<lote>[^/]+)/$',
        views.ajax_endereco_lote, name='endereco_lote__ajax'),

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

    url(r'^rearrumar/$', views.Rearrumar.as_view(), name='rearrumar'),
    url(r'^rearrumar/m/$',
        views.RearrumarMobile.as_view(), name='rearrumar_m'),

    url(r'^retirar/$', views.Retirar.as_view(), name='retirar'),
    url(r'^retirar/m/$', views.RetirarMobile.as_view(), name='retirar_m'),

    url(r'^retirar_parcial/$',
        views.RetirarParcial.as_view(), name='retirar_parcial'),
    url(r'^retirar_parcial/m/$',
        views.RetirarParcialMobile.as_view(), name='retirar_parcial_m'),

    url(r'^movimentacao/$', views.movimentacao, name='movimentacao'),

    url(r'^etiq_solicitacoes/?$',
        views.EtiquetasSolicitacoes.as_view(), name='etiq_solicitacoes'),

    url(r'^enderecar/$', views.Enderecar.as_view(), name='enderecar'),
    url(r'^enderecar/m/$',
        views.EnderecarMobile.as_view(), name='enderecar_m'),

    url(r'^troca_endereco/$',
        views.TrocaEndereco.as_view(), name='troca_endereco'),
    url(r'^troca_endereco/m/$',
        views.TrocaEnderecoMobile.as_view(), name='troca_endereco_m'),

]
