from django.urls import include, re_path

import cd.views as views
from cd.views import (
    admin_palete,
    add1palete,
    api_lote,
    api_palete,
    compara_apoio_systextil,
    confronta_qtd_lote,
    confronta_qtd_solicit,
    conteudo_local,
    endereca_grupo,
    endereco,
    endereco_imprime,
    endereco_conteudo_importa,
    esvazia_palete,
    lista_lotes_invent,
    localiza_lote,
    qtd_em_lote,
    palete,
    vizualiza_esvaziamento,
)
from cd.views.novo_modulo import (
    atividade_cd63,
    estoque,
    estoque_ficticio,
    etqs_parciais,
    finaliza_emp_op,
    disponibilidade,
    disponibilidade_ficticio,
    distribuicao,
    grade_estoque_totais,
    historico_lote,
    nao_enderecados,
    palete_solicitacao,
    solicitacao,
    solicitacoes,
    realoca_solicitacoes,
    visao_bloco,
    visao_bloco_detalhe,
    visao_bloco_lotes,
    visao_cd,
)
from cd.views.api.palete.print import PaletePrint
from cd.views.api.cancela_solicitacao import CancelSolicitacao


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

    re_path(r'^grade_estoque_totais/$',
        grade_estoque_totais.GradeEstoqueTotais.as_view(), name='grade_estoque_totais'),

    re_path(r'^historico/?$',
        views.Historico.as_view(), name='historico'),

    re_path(r'^historico/(?P<op>[^/]+)?$',
        views.Historico.as_view(), name='historico__get'),

    re_path(r'^historico_lote_old/(?P<lote>[^/]+)?$',
        views.HistoricoLote.as_view(), name='historico_lote_old'),

    re_path(r'^historico_lote/(?P<lote>[^/]+)?$',
        historico_lote.HistoricoLote.as_view(), name='historico_lote'),

    re_path(r'^atividade_cd63$',
        atividade_cd63.AtividadeCD63.as_view(), name='atividade_cd63'),

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

    re_path(r'^etqs_parciais/?$',
        etqs_parciais.EtiquetasParciais.as_view(), name='etqs_parciais'),

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

    re_path(r'^add1palete/$',
        add1palete.Add1Palete.as_view(), name='add1palete'),

    re_path(r'^api/cancela_solicitacao/(?P<solicitacao>[^/]+)/$',
        CancelSolicitacao.as_view(), name='cancela_solicitacao'),

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

    re_path(r'^api/endereco_print/(?P<copias>.+)/(?P<endereco>.+)$',
        endereco_imprime.EnderecoPrint1.as_view(), name='endereco_print'),

    re_path(r'^endereco_conteudo_importa/$',
        endereco_conteudo_importa.EnderecoImporta.as_view(),
        name='endereco_conteudo_importa'),

    re_path(r'^compara_apoio_systextil/$',
        compara_apoio_systextil.ComparaApoioSystextil.as_view(),
        name='compara_apoio_systextil'),

    re_path(r'^conteudo_local/(?P<local>[^/]+)?$',
        conteudo_local.ConteudoLocal.as_view(),
        name='conteudo_local'),

    re_path(r'^coletor/$', views.coletor, name='coletor'),

    re_path(r'^localiza_lote/(?P<lote>[^/]+)?$',
        localiza_lote.LocalizaLote.as_view(),
        name='localiza_lote'),

    re_path(r'^esvazia_palete/$',
        esvazia_palete.EsvaziaPalete.as_view(),
        name='esvazia_palete'),

    re_path(r'^vizualiza_esvaziamento/(?P<palete>[^/]+)/(?P<data_versao>[^/]+)/$',
        vizualiza_esvaziamento.VisualizaEsvaziamento.as_view(),
        name='vizualiza_esvaziamento'),

    re_path(r'^api/retira_lote/(?P<lote>.+)$',
        api_lote.retira_lote, name='retira_lote'),

    re_path(r'^palete/$',
        palete.Palete.as_view(), name='palete'),

    re_path(r'^endereca_grupo/$',
        endereca_grupo.EnderecaGrupo.as_view(), name='endereca_grupo'),

    re_path(r'^novo/solicitacao/(?P<solicitacao>[^/]+)$',
        solicitacao.Solicitacao.as_view(), name='novo_solicitacao'),

    re_path(r'^novo/solicitacoes/$',
        solicitacoes.Solicitacoes.as_view(), name='novo_solicitacoes'),

    re_path(r'^novo/realoca_solicitacoes/$',
        realoca_solicitacoes.RealocaSolicitacoes.as_view(), name='realoca_solicitacoes'),

    re_path(r'^novo/estoque/$',
        estoque.NovoEstoque.as_view(), name='novo_estoque'),

    re_path(r'^novo/palete_solicitacao/$',
        palete_solicitacao.PaleteSolicitacaoView.as_view(), name='palete_solicitacao'),

    re_path(r'^novo/estoque_ficticio/$',
        estoque_ficticio.NovoEstoqueFicticio.as_view(), name='novo_estoque_ficticio'),

    re_path(r'^novo/finaliza_emp_op/$',
        finaliza_emp_op.FinalizaEmpenhoOp.as_view(), name='finaliza_emp_op'),

    re_path(r'^novo/visao_bloco/(?P<bloco>[^/]+)$',
        visao_bloco.VisaoBloco.as_view(), name='novo_visao_bloco__get'),

    re_path(r'^novo/visao_bloco_detalhe/(?P<bloco>[^/]+)$',
        visao_bloco_detalhe.VisaoBlocoDetalhe.as_view(),
        name='visao_bloco_detalhe__get'),

    re_path(r'^novo/visao_bloco_lotes/(?P<bloco>[^/]+)$',
        visao_bloco_lotes.VisaoBlocoLotes.as_view(),
        name='visao_bloco_lotes__get'),

    re_path(r'^novo/visao_cd/$',
        visao_cd.VisaoCd.as_view(), name='novo_visao_cd'),

    re_path(r'^qtd_em_lote/$',
        qtd_em_lote.QtdEmLote.as_view(),
        name='qtd_em_lote'),

    re_path(r'^confronta_qtd_lote/(?P<up>.+)?/?$',
        confronta_qtd_lote.ConfrontaQtdLote.as_view(),
        name='confronta_qtd_lote'),

    re_path(r'^lista_lotes_invent/$',
        lista_lotes_invent.ListaLoteInvent.as_view(),
        name='lista_lotes_invent'),

    re_path(r'^confronta_qtd_solicit/(?P<up>.+)?/?$',
        confronta_qtd_solicit.ConfrontaQtdSolicit.as_view(),
        name='confronta_qtd_solicit'),

    re_path(r'^nao_enderecados/(?P<up>.+)?/?$',
        nao_enderecados.NaoEnderecados.as_view(),
        name='nao_enderecados'),

    re_path(r'^disponibilidade/$',
        disponibilidade.Disponibilidade.as_view(), name='disponibilidade'),

    re_path(r'^disponibilidade_ficticio/$',
        disponibilidade_ficticio.DisponibilidadeFicticio.as_view(), name='disponibilidade_ficticio'),

    re_path(r'^distribuicao/$',
        distribuicao.Distribuicao.as_view(), name='distribuicao'),

]
