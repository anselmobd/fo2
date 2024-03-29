from django.urls import include, path, re_path

import lotes.views as views
from lotes.views import (
    lote,
    perda,
    por_celula,
    prepara_pedido_compra_matriz,
    prepara_pedido_corte,
    prepara_pedido_op_cortada,
)
from lotes.views.ajax import produzir_modelo_grade as ajax_produzir_modelo_grade
from lotes.views.ajax.produz_lote import ProduzLote
from lotes.views.analise import produzir_grade_empenho
from lotes.views.ops import seq_erro
from lotes.views.pedido import cancela_pedido
from lotes.views.pedido.rastreabilidade import RastreabilidadeView

app_name = 'producao'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    path('corte/', include('lotes.urls.corte')),
    path('parametros/', include('lotes.urls.parametros')),
    path('impressao/', include('lotes.urls.impressao')),
    path('analise/', include('lotes.urls.analise')),

    re_path(r'^a_produzir/$', views.AProduzir.as_view(), name='a_produzir'),

    re_path(r'^ajax/altera_direito_estagio/(?P<id>[^/]+)/$',
        views.altera_direito_estagio, name='altera_direito_estagio'),

    re_path(r'^ajax/estoque_depositos_modelo/(?P<modelo>[^/]+)/$',
        views.estoque_depositos_modelo, name='estoque_depositos_modelo'),
    re_path(r'^ajax/estoque_depositos_modelo/(?P<modelo>[^/]+)/'
        r'(?P<filtra>[^/]+)/$',
        views.estoque_depositos_modelo, name='estoque_depositos_modelo__get2'),

    re_path(r'^ajax/op_producao_modelo/(?P<modelo>[^/]+)/$',
        views.op_producao_modelo, name='op_producao_modelo'),

    re_path(r'^ajax/pedido_lead_modelo/(?P<modelo>[^/]+)/$',
        views.pedido_lead_modelo, name='pedido_lead_modelo'),

    re_path(r'^analise/grade_pedidos/$',
        views.analise.GradePedidos.as_view(), name='analise_grade_pedidos'),

    re_path(r'^analise/grade_produzir/$',
        views.analise.GradeProduzir.as_view(), name='analise_grade_produzir'),

    re_path(r'^analise/grade_produzir_modelo/$',
        views.analise.GradeProduzirSoModelo.as_view(), name='analise_grade_produzir_modelo'),

    re_path(r'^analise/produzir_grade_empenho/$',
        produzir_grade_empenho.ProduzirGradeEmpenho.as_view(),
        name='analise_produzir_grade_empenho'),

    re_path(r'^analise/periodo_alter/$',
        views.analise.PeriodoAlter.as_view(), name='analise_periodo_alter'),
    re_path(r'^analise/periodo_alter/(?P<periodo>\d+)/$',
        views.analise.PeriodoAlter.as_view(),
        name='analise_periodo_alter__get'),

    re_path(r'^analise/produzir_modelo_grade/$',
        views.analise.ProduzirModeloGrade.as_view(),
        name='produzir_modelo_grade'),

    re_path(r'^ajax/produzir_modelo_grade/(?P<modelo>[^/]+)/$',
        ajax_produzir_modelo_grade.produzir_modelo_grade,
        name='ajax_produzir_modelo_grade'),

    re_path(r'^busca_op/$', views.ord_prod.BuscaOP.as_view(), name='busca_op'),
    re_path(r'^busca_op/(?P<ref>.+)/$', views.ord_prod.BuscaOP.as_view(),
        name='busca_op__get'),

    re_path(r'^componentes_de_op/$', views.ComponentesDeOp.as_view(),
        name='componentes_de_op'),
    re_path(r'^componentes_de_op/(?P<op>\d+)/$', views.ComponentesDeOp.as_view(),
        name='componentes_de_op__get'),

    re_path(r'^conserto/$',
        views.OpConserto.as_view(), name='conserto'),

    re_path(r'^conserto_lote/ajax/(?P<lote>[^/]+)/(?P<estagio>[^/]+)/'
        r'(?P<in_out>[^/]+)/(?P<qtd_a_mover>[^/]+)?/?$',
        views.lote.ajax_conserto_lote, name='conserto_lote__ajax'),

    re_path(r'^corrige_sequenciamento/$',
        views.ops.corrige_seq.CorrigeSequenciamento.as_view(), name='corrige_sequenciamento'),

    re_path(r'^distribuicao/$',
        views.Distribuicao.as_view(), name='distribuicao'),

    re_path(r'^edita_respons/$', views.analise.respons_edit, name='edita_respons'),

    re_path(r'^expedicao/$', views.pedido.Expedicao.as_view(), name='expedicao'),
    re_path(r'^expedicao/(?P<cliente>\d+)/(?P<pedido_cliente>.+)/$',
        views.pedido.Expedicao.as_view(), name='expedicao__get'),

    re_path(r'^lista_lotes/$',
        views.ListaLotes.as_view(), name='lista_lotes'),

    re_path(r'^meta_giro/$',
        views.analise.MetaGiro.as_view(), name='meta_giro'),

    re_path(r'^meta_total/$',
        views.analise.MetaTotal.as_view(), name='meta_total'),

    re_path(r'^op/$', views.ops.op.Op.as_view(), name='op'),
    re_path(r'^op/(?P<op>\d+)/$', views.ops.op.Op.as_view(), name='op__get'),

    re_path(
        r'^reativa_op/(?P<op>\d+)/$',
        views.ops.reativa_op.ReativaOp.as_view(),
        name='reativa_op__get'
    ),

    re_path(r'^op/historico/(?P<op>\d+)?/?$', views.ops.historico.Historico.as_view(),
        name='historico_op'),

    re_path(r'^op/seq_erro/?$', seq_erro.view,
        name='op_seq_erro'),

    re_path(r'^op_caixa/$', views.OpCaixa.as_view(), name='op_caixa'),
    re_path(r'^op_caixa/(?P<op>\d+)/$',
        views.OpCaixa.as_view(), name='op_caixa__get'),

    re_path(r'^op_pendente/$', views.OpPendente.as_view(), name='op_pendente'),
    re_path(r'^op_pendente/(?P<estagio>.+)/$', views.OpPendente.as_view(),
        name='op_pendente__get'),

    re_path(r'^os/$', views.Os.as_view(), name='os'),
    re_path(r'^os/(?P<os>\d+)/$', views.Os.as_view(), name='os__get'),

    re_path(r'^pedido/$', views.pedido.Pedido.as_view(), name='pedido'),
    re_path(r'^pedido/(?P<pedido>\d+)/$', views.pedido.Pedido.as_view(),
        name='pedido__get'),

    re_path(
        r'^reativa_pedido/(?P<pedido>\d+)/$',
        views.pedido.reativa_pedido.ReativaPedido.as_view(),
        name='reativa_pedido__get'
    ),

    re_path(
        r'^cancela_pedido/(?P<pedido>\d+)/$',
        cancela_pedido.CancelaPedido.as_view(),
        name='cancela_pedido__get'
    ),

    re_path(r'^pedido/historico$', views.pedido.Historico.as_view(), name='pedido_historico'),
    re_path(r'^pedido/historico/(?P<pedido>\d+)/$', views.pedido.Historico.as_view(),
        name='pedido_historico__get'),

    re_path(r'^faturavel_modelo/$',
        views.pedido.FaturavelModelo.as_view(),
        name='faturavel_modelo'),
    re_path(r'^faturavel_modelo/(?P<modelo>[^/]+)/$',
        views.pedido.FaturavelModelo.as_view(),
        name='faturavel_modelo__get'),

    re_path(r'^perda/$',
        perda.OpPerda.as_view(), name='perda'),

    re_path(r'^lote/$', lote.Lote.as_view(), name='lote'),
    re_path(r'^lote/(?P<lote>\d+)/$', lote.Lote.as_view(),
        name='lote__get'),

    re_path(r'^por_celula/$',
        por_celula.PorCelula.as_view(), name='por_celula'),

    re_path(r'^quant_estagio/$',
        views.analise.QuantEstagio.as_view(), name='quant_estagio'),
    re_path(r'^quant_estagio/(?P<estagio>\d+)/$',
        views.analise.QuantEstagio.as_view(), name='quant_estagio__get'),

    re_path(
        r'^rastreabilidade/$', 
        RastreabilidadeView.as_view(),
        name='rastreabilidade'
    ),

    re_path(
        r'^rastreabilidade/(?P<pedido>\d+)/$',
        RastreabilidadeView.as_view(),
        name='rastreabilidade__get'
    ),

    re_path(r'^respons/$', views.analise.respons, name='respons'),

    re_path(r'^respons_todos/$', views.analise.respons_todos,
        name='respons_todos'),

    re_path(r'^ajax/prepara_pedido_corte/(?P<data>[^/]+)/(?P<cliente>[^/]+)/(?P<pedido>[^/]+)/$',
        prepara_pedido_corte.PreparaPedidoCorte.as_view(), name='prepara_pedido_corte'),

    re_path(r'^ajax/prepara_pedido_op_cortada/(?P<data>[^/]+)/(?P<cliente>[^/]+)/(?P<pedido>[^/]+)/$',
        prepara_pedido_op_cortada.PreparaPedidoOpCortada.as_view(), name='prepara_pedido_op_cortada'),

    re_path(r'^ajax/prepara_pedido_compra_matriz/(?P<pedido_filial>[^/]+)/$',
        prepara_pedido_compra_matriz.PreparaPedidoCompraMatriz.as_view(),
        name='prepara_pedido_compra_matriz'),

    re_path(r'^ajax/produz_lote/(?P<lote>[^/]+)/(?P<estagio>[^/]+)/(?P<qtd>[^/]+)/$',
        ProduzLote.as_view(),
        name='produz_lote'),

    re_path(r'^ajax/produz_lote/(?P<lote>[^/]+)/(?P<estagio>[^/]+)/(?P<qtd>[^/]+)/(?P<programa>[^/]+)/$',
        ProduzLote.as_view(),
        name='produz_lote_programa'),

    re_path(r'^totais_estagio/$',
        views.analise.TotalEstagio.as_view(), name='totais_estagio'),
]
