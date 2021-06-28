from django.urls import re_path

from lotes.views import parametros

from . import views


app_name = 'producao'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    re_path(r'^posicao/$', views.Posicao.as_view(), name='posicao'),
    re_path(r'^posicao/(?P<lote>\d+)/$', views.Posicao.as_view(),
        name='posicao__get'),

    re_path(r'^respons/$', views.analise.respons, name='respons'),

    re_path(r'^respons_todos/$', views.analise.respons_todos,
        name='respons_todos'),

    re_path(r'^edita_respons/$', views.analise.respons_edit, name='edita_respons'),

    re_path(r'^ajax/altera_direito_estagio/(?P<id>[^/]+)/$',
        views.altera_direito_estagio, name='altera_direito_estagio'),

    re_path(r'^busca_op/$', views.ord_prod.BuscaOP.as_view(), name='busca_op'),
    re_path(r'^busca_op/(?P<ref>.+)/$', views.ord_prod.BuscaOP.as_view(),
        name='busca_op__get'),

    re_path(r'^op/$', views.Op.as_view(), name='op'),
    re_path(r'^op/(?P<op>\d+)/$', views.Op.as_view(), name='op__get'),

    re_path(r'^componentes_de_op/$', views.ComponentesDeOp.as_view(),
        name='componentes_de_op'),
    re_path(r'^componentes_de_op/(?P<op>\d+)/$', views.ComponentesDeOp.as_view(),
        name='componentes_de_op__get'),

    re_path(r'^os/$', views.Os.as_view(), name='os'),
    re_path(r'^os/(?P<os>\d+)/$', views.Os.as_view(), name='os__get'),

    re_path(r'^analise/periodo_alter/$',
        views.analise.PeriodoAlter.as_view(), name='analise_periodo_alter'),
    re_path(r'^analise/periodo_alter/(?P<periodo>\d+)/$',
        views.analise.PeriodoAlter.as_view(),
        name='analise_periodo_alter__get'),

    re_path(r'^analise/dtcorte_alter/$',
        views.analise.DtCorteAlter.as_view(), name='analise_dtcorte_alter'),
    re_path(r'^analise/dtcorte_alter/(?P<data>\d+)/$',
        views.analise.DtCorteAlter.as_view(),
        name='analise_dtcorte_alter__get'),

    re_path(r'^op_pendente/$', views.OpPendente.as_view(), name='op_pendente'),
    re_path(r'^op_pendente/(?P<estagio>.+)/$', views.OpPendente.as_view(),
        name='op_pendente__get'),

    re_path(r'^imprime_lotes/$',
        views.ImprimeLotes.as_view(), name='imprime_lotes'),

    re_path(r'^imprime_ob1/$',
        views.ImprimeOb1.as_view(), name='imprime_ob1'),

    re_path(r'^imprime_pacote3lotes/$',
        views.ImprimePacote3Lotes.as_view(), name='imprime_pacote3lotes'),

    re_path(r'^imprime_caixa_lotes/$',
        views.ImprimeCaixaLotes.as_view(), name='imprime_caixa_lotes'),

    re_path(r'^impressora_termica/$',
        views.impressoraTermica, name='impressora_termica'),

    re_path(r'^pedido/$', views.pedido.Pedido.as_view(), name='pedido'),
    re_path(r'^pedido/(?P<pedido>\d+)/$', views.pedido.Pedido.as_view(),
        name='pedido__get'),

    re_path(r'^expedicao/$', views.pedido.Expedicao.as_view(), name='expedicao'),

    re_path(r'^op_caixa/$', views.OpCaixa.as_view(), name='op_caixa'),
    re_path(r'^op_caixa/(?P<op>\d+)/$',
        views.OpCaixa.as_view(), name='op_caixa__get'),

    re_path(r'^distribuicao/$',
        views.Distribuicao.as_view(), name='distribuicao'),

    re_path(r'^conserto/$',
        views.OpConserto.as_view(), name='conserto'),

    re_path(r'^perda/$',
        views.OpPerda.as_view(), name='perda'),

    re_path(r'^imprime_tag/$',
        views.ImprimeTag.as_view(), name='imprime_tag'),

    re_path(r'^lista_lotes/$',
        views.ListaLotes.as_view(), name='lista_lotes'),

    re_path(r'^corrige_sequenciamento/$',
        views.CorrigeSequenciamento.as_view(), name='corrige_sequenciamento'),

    re_path(r'^quant_estagio/$',
        views.analise.QuantEstagio.as_view(), name='quant_estagio'),
    re_path(r'^quant_estagio/(?P<estagio>\d+)/$',
        views.analise.QuantEstagio.as_view(), name='quant_estagio__get'),

    re_path(r'^totais_estagio/$',
        views.analise.TotalEstagio.as_view(), name='totais_estagio'),

    re_path(r'^lead_colecao/(?P<id>[^/]+)?$',
        views.LeadColecao.as_view(), name='lead_colecao'),

    re_path(r'^lote_min_colecao/(?P<id>[^/]+)?$',
        views.LoteMinColecao.as_view(), name='lote_min_colecao'),

    re_path(r'^regras_lote_min_tamanho/(?P<id>[^/]+)?$',
        views.RegrasLoteMinTamanho.as_view(), name='regras_lote_min_tamanho'),

    re_path(r'^regras_lote_caixa/$',
        views.RegrasLoteCaixa.as_view(), name='regras_lote_caixa'),
    re_path(r'^regras_lote_caixa/(?P<colecao>[^/]+)?/(?P<referencia>[^/]+)?/(?P<ead>[^/]+)?/$',
        views.RegrasLoteCaixa.as_view(), name='regras_lote_caixa__get'),

    re_path(r'^meta_giro/$',
        views.MetaGiro.as_view(), name='meta_giro'),

    re_path(r'^meta_total/$',
        views.MetaTotal.as_view(), name='meta_total'),

    re_path(r'^pedido_faturavel_modelo/$',
        views.pedido.PedidoFaturavelModelo.as_view(),
        name='pedido_faturavel_modelo'),
    re_path(r'^pedido_faturavel_modelo/(?P<modelo>[^/]+)/$',
        views.pedido.PedidoFaturavelModelo.as_view(),
        name='pedido_faturavel_modelo__get'),

    re_path(r'^a_produzir/$', views.AProduzir.as_view(), name='a_produzir'),

    re_path(r'^analise/produzir_modelo_grade/$',
        views.analise.ProduzirModeloGrade.as_view(),
        name='produzir_modelo_grade'),

    re_path(r'^ajax/op_producao_modelo/(?P<modelo>[^/]+)/$',
        views.op_producao_modelo, name='op_producao_modelo'),

    re_path(r'^ajax/pedido_lead_modelo/(?P<modelo>[^/]+)/$',
        views.pedido_lead_modelo, name='pedido_lead_modelo'),

    re_path(r'^ajax/estoque_depositos_modelo/(?P<modelo>[^/]+)/$',
        views.estoque_depositos_modelo, name='estoque_depositos_modelo'),
    re_path(r'^ajax/estoque_depositos_modelo/(?P<modelo>[^/]+)/'
        r'(?P<filtra>[^/]+)/$',
        views.estoque_depositos_modelo, name='get2__estoque_depositos_modelo'),

    re_path(r'^grade_produzir/$',
        views.GradeProduzirOld.as_view(), name='grade_produzir'),

    re_path(r'^analise/grade_produzir/$',
        views.analise.GradeProduzir.as_view(), name='analise_grade_produzir'),

    re_path(r'^analise/grade_produzir_modelo/$',
        views.analise.GradeProduzirSoModelo.as_view(), name='analise_grade_produzir_modelo'),

    re_path(r'^analise/grade_pedidos/$',
        views.analise.GradePedidos.as_view(), name='analise_grade_pedidos'),

    re_path(r'^conserto_lote/ajax/(?P<lote>[^/]+)/(?P<estagio>[^/]+)/'
        r'(?P<in_out>[^/]+)/(?P<qtd_a_mover>[^/]+)?/?$',
        views.lote.ajax_conserto_lote, name='conserto_lote__ajax'),

    re_path(r'^pedido/historico$', views.pedido.Historico.as_view(), name='pedido_historico'),
    re_path(r'^pedido/historico/(?P<pedido>\d+)/$', views.pedido.Historico.as_view(),
        name='pedido_historico__get'),

    # OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD

    re_path(r'^posicao.old/$', views.posicaoOri, name='posicao.old'),

    re_path(r'^posicao.old/ajax/detalhes_lote/(\d{9})/$',
        views.detalhes_lote, name='posicao.old_detalhes_lote'),
]
