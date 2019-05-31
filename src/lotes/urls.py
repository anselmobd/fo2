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

    # OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD

    url(r'^posicao.old/$', views.posicaoOri, name='posicao.old'),

    url(r'^posicao.old/ajax/detalhes_lote/(\d{9})/$',
        views.detalhes_lote, name='posicao.old_detalhes_lote'),
]
