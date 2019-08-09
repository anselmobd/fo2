from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^posicao/$', views.Posicao.as_view(), name='posicao'),
    url(r'^posicao/(?P<lote>\d+)/$', views.Posicao.as_view(),
        name='posicao__get'),

    url(r'^respons/$', views.respons, name='respons'),

    url(r'^responsavel/$', views.responsTodos, name='respons_todos'),

    url(r'^busca_op/$', views.BuscaOP.as_view(), name='busca_op'),
    url(r'^busca_op/(?P<ref>.+)/$', views.BuscaOP.as_view(),
        name='busca_op__get'),

    url(r'^op/$', views.Op.as_view(), name='op'),
    url(r'^op/(?P<op>\d+)/$', views.Op.as_view(), name='op__get'),

    url(r'^componentes_de_op/$', views.ComponentesDeOp.as_view(),
        name='componentes_de_op'),
    url(r'^componentes_de_op/(?P<op>\d+)/$', views.ComponentesDeOp.as_view(),
        name='componentes_de_op__get'),

    url(r'^os/$', views.Os.as_view(), name='os'),
    url(r'^os/(?P<os>\d+)/$', views.Os.as_view(), name='os__get'),

    url(r'^an_periodo_alter/$',
        views.AnPeriodoAlter.as_view(), name='an_periodo_alter'),
    url(r'^an_periodo_alter/(?P<periodo>\d+)/$',
        views.AnPeriodoAlter.as_view(), name='an_periodo_alter__get'),

    url(r'^an_dtcorte_alter/$',
        views.AnDtCorteAlter.as_view(), name='an_dtcorte_alter'),
    url(r'^an_dtcorte_alter/(?P<data>\d+)/$',
        views.AnDtCorteAlter.as_view(), name='an_dtcorte_alter__get'),

    url(r'^op_pendente/$', views.OpPendente.as_view(), name='op_pendente'),
    url(r'^op_pendente/(?P<estagio>.+)/$', views.OpPendente.as_view(),
        name='op_pendente__get'),

    url(r'^imprime_lotes/$',
        views.ImprimeLotes.as_view(), name='imprime_lotes'),

    url(r'^imprime_pacote3lotes/$',
        views.ImprimePacote3Lotes.as_view(), name='imprime_pacote3lotes'),

    url(r'^impressora_termica/$',
        views.impressoraTermica, name='impressora_termica'),

    url(r'^pedido/$', views.Pedido.as_view(), name='pedido'),
    url(r'^pedido/(?P<pedido>\d+)/$', views.Pedido.as_view(),
        name='pedido__get'),

    url(r'^expedicao/$', views.Expedicao.as_view(), name='expedicao'),

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
        views.QuantEstagio.as_view(), name='quant_estagio'),
    url(r'^quant_estagio/(?P<estagio>\d+)/$',
        views.QuantEstagio.as_view(), name='quant_estagio__get'),

    url(r'^totais_estagio/$',
        views.TotalEstagio.as_view(), name='totais_estagio'),

    url(r'^lead_colecao/(?P<id>[^/]+)?$',
        views.LeadColecao.as_view(), name='lead_colecao'),

    url(r'^lote_min_colecao/(?P<id>[^/]+)?$',
        views.LoteMinColecao.as_view(), name='lote_min_colecao'),

    url(r'^meta_giro/$',
        views.MetaGiro.as_view(), name='meta_giro'),

    url(r'^busca_pedido/$', views.BuscaPedido.as_view(), name='busca_pedido'),

    url(r'^a_produzir/$', views.AProduzir.as_view(), name='a_produzir'),

    url(r'^ajax/op_producao_modelo/(?P<modelo>[^/]+)/$',
        views.op_producao_modelo, name='op_producao_modelo'),

    url(r'^ajax/pedido_lead_modelo/(?P<modelo>[^/]+)/$',
        views.pedido_lead_modelo, name='pedido_lead_modelo'),

    url(r'^grade_produzir/$',
        views.GradeProduzir.as_view(), name='grade_produzir'),

    # OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD

    url(r'^posicao.old/$', views.posicaoOri, name='posicao.old'),

    url(r'^posicao.old/ajax/detalhes_lote/(\d{9})/$',
        views.detalhes_lote, name='posicao.old_detalhes_lote'),
]
