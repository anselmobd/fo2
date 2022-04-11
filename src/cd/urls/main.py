from django.urls import include, re_path

import cd.views as views
from cd.views import (
    admin_palete,
    api_palete,
    compara_apoio_systextil,
    conteudo_local,
    endereco,
    endereco_imprime,
    endereco_conteudo_importa,
    esvazia_palete,
    localiza_lote,
)
from cd.views.api.palete.print import PaletePrint


app_name = 'cd'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    re_path(r'^s/$', views.teste_som, name='teste_som'),

    re_path(r'^atividade_cd/?$',
        views.AtividadeCD.as_view(), name='atividade_cd'),

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

    # re_path(r'^rearrumar/$', views.Rearrumar.as_view(), name='rearrumar'),
    # re_path(r'^rearrumar/m/$',
    #     views.RearrumarMobile.as_view(), name='rearrumar_m'),

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

    re_path(r'^admin_palete/$',
        admin_palete.AdminPalete.as_view(), name='admin_palete'),

    re_path(r'^api/palete_add/(?P<quant>.+)$',
        api_palete.palete_add, name='palete_add'),

    re_path(r'^api/palete_print/((?P<copias>.+)/)?(?P<code>.+)?$',
        PaletePrint.as_view(), name='palete_print'),

    re_path(r'^api/palete_printed/$',
        api_palete.palete_printed, name='palete_printed'),

    re_path(r'^endereco/$',
        endereco.Endereco.as_view(), name='endereco'),

    re_path(r'^endereco_imprime/$',
        endereco_imprime.EnderecoImprime.as_view(), name='endereco_imprime'),

    re_path(r'^endereco_conteudo_importa/$',
        endereco_conteudo_importa.EnderecoImporta.as_view(),
        name='endereco_conteudo_importa'),

    re_path(r'^compara_apoio_systextil/$',
        compara_apoio_systextil.ComparaApoioSystextil.as_view(),
        name='compara_apoio_systextil'),

    re_path(r'^conteudo_local/(?P<codigo>[^/]+)?$',
        conteudo_local.ConteudoLocal.as_view(),
        name='conteudo_local'),

    re_path(r'^coletor/$', views.coletor, name='coletor'),

    re_path(r'^localiza_lote/(?P<lote>[^/]+)?$',
        localiza_lote.LocalizaLote.as_view(),
        name='localiza_lote'),

    re_path(r'^esvazia_palete/$',
        esvazia_palete.EsvaziaPalete.as_view(),
        name='esvazia_palete'),

]
