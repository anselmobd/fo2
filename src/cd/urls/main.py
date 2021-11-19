from django.urls import include, re_path

import cd.views as views


app_name = 'cd'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    re_path(r'^s/$', views.teste_som, name='teste_som'),

    re_path(r'^estoque/(?P<ordem>.)/(?P<filtro>.+)/$',
        views.Estoque.as_view(), name='estoque_filtro'),
    re_path(r'^estoque/$', views.Estoque.as_view(), name='estoque'),

    re_path(r'^troca_local/$', views.menu_desligado, name='troca_local'),
    re_path(r'^troca_local_/$', views.TrocaLocal.as_view(), name='troca_local_'),

    re_path(r'^inconsist/(?P<ordem>.-?)/(?P<opini>-?\d+)/$',
        views.Inconsistencias.as_view(), name='inconsist_opini'),
    re_path(r'^inconsist/$', views.Inconsistencias.as_view(), name='inconsist'),

    re_path(r'^inconsist_detalhe/(?P<op>\d+)/$',
        views.InconsistenciasDetalhe.as_view(),
        name='inconsist_detalhe_op'),

    re_path(r'^visao_cd/$',
        views.VisaoCd.as_view(), name='visao_cd'),

    re_path(r'^visao_rua/(?P<rua>[^/]+)/$',
        views.VisaoRua.as_view(), name='visao_rua__get'),

    re_path(r'^visao_rua_detalhe/(?P<rua>[^/]+)/$',
        views.VisaoRuaDetalhe.as_view(), name='visao_rua_detalhe__get'),

    re_path(r'^solicitacoes/(?P<id>[^/]+)?$',
        views.Solicitacoes.as_view(), name='solicitacoes'),

    re_path(r'^ajax/libera_coleta_de_solicitacao/(?P<num>[^/]+)/$',
        views.libera_coleta_de_solicitacao,
        name='libera_coleta_de_solicitacao'),

    re_path(r'^solicitacao_detalhe/(?P<solicit_id>[^/]+)'
        '/(?P<acao>[^/]+)/(?P<id>[^/]+)$',
        views.SolicitacaoDetalhe.as_view(),
        name='solicitacao_detalhe__get3'),
    re_path(r'^solicitacao_detalhe/(?P<solicit_id>[^/]+)'
        '/(?P<acao>[^/]+)$',
        views.SolicitacaoDetalhe.as_view(),
        name='solicitacao_detalhe__get2'),
    re_path(r'^solicitacao_detalhe/(?P<solicit_id>[^/]+)',
        views.SolicitacaoDetalhe.as_view(), name='solicitacao_detalhe'),

    re_path(r'^solicita/(?P<solicitacao_id>[^/]+)/'
        '(?P<lote>[^/]+)/(?P<qtd>[^/]+)/$',
        views.solicita_lote, name='solicita_lote'),

    re_path(r'^endereco_lote/(?P<lote>[^/]+)?$', views.EnderecoLote.as_view(),
        name='endereco_lote'),

    re_path(r'^endereco_lote/ajax/(?P<lote>[^/]+)/$',
        views.ajax_endereco_lote, name='endereco_lote__ajax'),

    re_path(r'^grade_estoque/(?P<referencia>[^/]+)/(?P<detalhe>[^/]+)?/?$',
        views.Grade.as_view(), name='grade_estoque_detalhe'),
    re_path(r'^grade_estoque/(?P<referencia>[^/]+)?/?$',
        views.Grade.as_view(), name='grade_estoque'),

    re_path(r'^historico/?$',
        views.Historico.as_view(), name='historico'),

    re_path(r'^historico/(?P<op>[^/]+)?$',
        views.Historico.as_view(), name='historico__get'),

    re_path(r'^historico_lote/(?P<lote>[^/]+)?$',
        views.HistoricoLote.as_view(), name='historico_lote'),

    re_path(r'^rearrumar/$', views.Rearrumar.as_view(), name='rearrumar'),
    re_path(r'^rearrumar/m/$',
        views.RearrumarMobile.as_view(), name='rearrumar_m'),

    re_path(r'^retirar/$', views.Retirar.as_view(), name='retirar'),
    re_path(r'^retirar/m/$', views.RetirarMobile.as_view(), name='retirar_m'),

    re_path(r'^retirar_parcial/$',
        views.RetirarParcial.as_view(), name='retirar_parcial'),
    re_path(r'^retirar_parcial/m/$',
        views.RetirarParcialMobile.as_view(), name='retirar_parcial_m'),

    re_path(r'^movimentacao/$', views.movimentacao, name='movimentacao'),

    re_path(r'^etiq_solicitacoes/?$',
        views.EtiquetasSolicitacoes.as_view(), name='etiq_solicitacoes'),

    re_path(r'^enderecar/$', views.Enderecar.as_view(), name='enderecar'),
    re_path(r'^enderecar/m/$',
        views.EnderecarMobile.as_view(), name='enderecar_m'),

    re_path(r'^troca_endereco/$',
        views.TrocaEndereco.as_view(), name='troca_endereco'),
    re_path(r'^troca_endereco/m/$',
        views.TrocaEnderecoMobile.as_view(), name='troca_endereco_m'),

    re_path(r'^mapa/', include('cd.urls.mapa')),

]
