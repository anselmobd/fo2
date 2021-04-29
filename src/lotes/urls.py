from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^posicao/$', views.Posicao.as_view(), name='posicao'),
    url(r'^posicao/(?P<lote>\d+)/$', views.Posicao.as_view(),
        name='posicao__get'),

    url(r'^respons/$', views.analise.respons, name='respons'),

    url(r'^respons_todos/$', views.analise.respons_todos,
        name='respons_todos'),

    url(r'^edita_respons/$', views.analise.respons_edit, name='edita_respons'),

    url(r'^ajax/altera_direito_estagio/(?P<id>[^/]+)/$',
        views.altera_direito_estagio, name='altera_direito_estagio'),

    url(r'^busca_op/$', views.ord_prod.BuscaOP.as_view(), name='busca_op'),
    url(r'^busca_op/(?P<ref>.+)/$', views.ord_prod.BuscaOP.as_view(),
        name='busca_op__get'),

    url(r'^op/$', views.Op.as_view(), name='op'),
    url(r'^op/(?P<op>\d+)/$', views.Op.as_view(), name='op__get'),

    url(r'^componentes_de_op/$', views.ComponentesDeOp.as_view(),
        name='componentes_de_op'),
    url(r'^componentes_de_op/(?P<op>\d+)/$', views.ComponentesDeOp.as_view(),
        name='componentes_de_op__get'),

    url(r'^os/$', views.Os.as_view(), name='os'),
    url(r'^os/(?P<os>\d+)/$', views.Os.as_view(), name='os__get'),

    url(r'^analise/periodo_alter/$',
        views.analise.PeriodoAlter.as_view(), name='analise_periodo_alter'),
    url(r'^analise/periodo_alter/(?P<periodo>\d+)/$',
        views.analise.PeriodoAlter.as_view(),
        name='analise_periodo_alter__get'),

    url(r'^analise/dtcorte_alter/$',
        views.analise.DtCorteAlter.as_view(), name='analise_dtcorte_alter'),
    url(r'^analise/dtcorte_alter/(?P<data>\d+)/$',
        views.analise.DtCorteAlter.as_view(),
        name='analise_dtcorte_alter__get'),

    url(r'^op_pendente/$', views.OpPendente.as_view(), name='op_pendente'),
    url(r'^op_pendente/(?P<estagio>.+)/$', views.OpPendente.as_view(),
        name='op_pendente__get'),

    url(r'^imprime_lotes/$',
        views.ImprimeLotes.as_view(), name='imprime_lotes'),

    url(r'^imprime_ob1/$',
        views.ImprimeOb1.as_view(), name='imprime_ob1'),

    url(r'^imprime_pacote3lotes/$',
        views.ImprimePacote3Lotes.as_view(), name='imprime_pacote3lotes'),

    url(r'^impressora_termica/$',
        views.impressoraTermica, name='impressora_termica'),

    url(r'^pedido/$', views.pedido.Pedido.as_view(), name='pedido'),
    url(r'^pedido/(?P<pedido>\d+)/$', views.pedido.Pedido.as_view(),
        name='pedido__get'),

    url(r'^expedicao/$', views.pedido.Expedicao.as_view(), name='expedicao'),

    url(r'^op_caixa/$', views.OpCaixa.as_view(), name='op_caixa'),
    url(r'^op_caixa/(?P<op>\d+)/$',
        views.OpCaixa.as_view(), name='op_caixa__get'),

    url(r'^distribuicao/$',
        views.Distribuicao.as_view(), name='distribuicao'),

    url(r'^conserto/$',
        views.OpConserto.as_view(), name='conserto'),

    url(r'^perda/$',
        views.OpPerda.as_view(), name='perda'),

    url(r'^imprime_tag/$',
        views.ImprimeTag.as_view(), name='imprime_tag'),

    url(r'^lista_lotes/$',
        views.ListaLotes.as_view(), name='lista_lotes'),

    url(r'^corrige_sequenciamento/$',
        views.CorrigeSequenciamento.as_view(), name='corrige_sequenciamento'),

    url(r'^quant_estagio/$',
        views.analise.QuantEstagio.as_view(), name='quant_estagio'),
    url(r'^quant_estagio/(?P<estagio>\d+)/$',
        views.analise.QuantEstagio.as_view(), name='quant_estagio__get'),

    url(r'^totais_estagio/$',
        views.analise.TotalEstagio.as_view(), name='totais_estagio'),

    url(r'^lead_colecao/(?P<id>[^/]+)?$',
        views.LeadColecao.as_view(), name='lead_colecao'),

    url(r'^lote_min_colecao/(?P<id>[^/]+)?$',
        views.LoteMinColecao.as_view(), name='lote_min_colecao'),

    url(r'^regras_lote_min_tamanho/(?P<id>[^/]+)?$',
        views.RegrasLoteMinTamanho.as_view(), name='regras_lote_min_tamanho'),

    url(r'^meta_giro/$',
        views.MetaGiro.as_view(), name='meta_giro'),

    url(r'^meta_total/$',
        views.MetaTotal.as_view(), name='meta_total'),

    url(r'^pedido_faturavel_modelo/$',
        views.pedido.PedidoFaturavelModelo.as_view(),
        name='pedido_faturavel_modelo'),
    url(r'^pedido_faturavel_modelo/(?P<modelo>[^/]+)/$',
        views.pedido.PedidoFaturavelModelo.as_view(),
        name='pedido_faturavel_modelo__get'),

    url(r'^a_produzir/$', views.AProduzir.as_view(), name='a_produzir'),

    url(r'^analise/produzir_modelo_grade/$',
        views.analise.ProduzirModeloGrade.as_view(),
        name='produzir_modelo_grade'),

    url(r'^ajax/op_producao_modelo/(?P<modelo>[^/]+)/$',
        views.op_producao_modelo, name='op_producao_modelo'),

    url(r'^ajax/pedido_lead_modelo/(?P<modelo>[^/]+)/$',
        views.pedido_lead_modelo, name='pedido_lead_modelo'),

    url(r'^ajax/estoque_depositos_modelo/(?P<modelo>[^/]+)/$',
        views.estoque_depositos_modelo, name='estoque_depositos_modelo'),
    url(r'^ajax/estoque_depositos_modelo/(?P<modelo>[^/]+)/'
        r'(?P<filtra>[^/]+)/$',
        views.estoque_depositos_modelo, name='get2__estoque_depositos_modelo'),

    url(r'^grade_produzir/$',
        views.GradeProduzirOld.as_view(), name='grade_produzir'),

    url(r'^analise/grade_produzir/$',
        views.analise.GradeProduzir.as_view(), name='analise_grade_produzir'),

    url(r'^analise/grade_pedidos/$',
        views.analise.GradePedidos.as_view(), name='analise_grade_pedidos'),

    url(r'^conserto_lote/ajax/(?P<lote>[^/]+)/(?P<estagio>[^/]+)/'
        r'(?P<in_out>[^/]+)/(?P<qtd_a_mover>[^/]+)?/?$',
        views.lote.ajax_conserto_lote, name='conserto_lote__ajax'),

    url(r'^pedido/historico$', views.pedido.Historico.as_view(), name='pedido_historico'),
    url(r'^pedido/historico/(?P<pedido>\d+)/$', views.pedido.Historico.as_view(),
        name='pedido_historico__get'),

    # OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD

    url(r'^posicao.old/$', views.posicaoOri, name='posicao.old'),

    url(r'^posicao.old/ajax/detalhes_lote/(\d{9})/$',
        views.detalhes_lote, name='posicao.old_detalhes_lote'),
]
