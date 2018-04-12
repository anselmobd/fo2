from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='lotes'),

    url(r'^posicao/$', views.Posicao.as_view(), name='posicao'),
    url(r'^posicao/(?P<lote>\d+)/$', views.Posicao.as_view(),
        name='posicao_lote'),

    url(r'^posicao2/$', views.Posicao2.as_view(), name='posicao2'),
    url(r'^posicao2/(?P<lote>\d+)/$', views.Posicao2.as_view(),
        name='posicao2_lote'),

    url(r'^respons/$', views.respons, name='respons'),
    url(r'^responsavel/$', views.responsTodos, name='respons_todos'),

    url(r'^op/$', views.Op.as_view(), name='op'),
    url(r'^op/(?P<op>\d+)/$', views.Op.as_view(), name='op_op'),

    url(r'^os/$', views.Os.as_view(), name='os'),
    url(r'^os/(?P<os>\d+)/$', views.Os.as_view(), name='os_os'),

    url(r'^an_periodo_alter/$',
        views.AnPeriodoAlter.as_view(), name='an_periodo_alter'),
    url(r'^an_periodo_alter/(?P<periodo>\d+)/$',
        views.AnPeriodoAlter.as_view(), name='an_periodo_alter_periodo'),

    url(r'^an_dtcorte_alter/$',
        views.AnDtCorteAlter.as_view(), name='an_dtcorte_alter'),
    url(r'^an_dtcorte_alter/(?P<data>\d+)/$',
        views.AnDtCorteAlter.as_view(), name='an_dtcorte_alter_dtcorte'),

    url(r'^op_pendente/$', views.OpPendente.as_view(), name='op_pendente'),
    url(r'^op_pendente/(?P<estagio>.+)/$', views.OpPendente.as_view(),
        name='op_pendente_estagio'),

    url(r'^imprime_lotes/$',
        views.ImprimeLotes.as_view(), name='imprime_lotes'),

    url(r'^imprime_pacote3lotes/$',
        views.ImprimePacote3Lotes.as_view(), name='imprime_pacote3lotes'),

    url(r'^impressora_termica/$',
        views.impressoraTermica, name='impressora_termica'),

    url(r'^pedido/$', views.Pedido.as_view(), name='pedido'),
    url(r'^pedido/(?P<pedido>\d+)/$', views.Pedido.as_view(),
        name='pedido_pedido'),

    url(r'^op_caixa/$', views.OpCaixa.as_view(), name='op_caixa'),
    url(r'^op_caixa/(?P<op>\d+)/$',
        views.OpCaixa.as_view(), name='op_caixa_op'),

    # OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD

    url(r'^posicao.old/$', views.posicaoOri, name='posicao.old'),
    url(r'^posicao.old/ajax/detalhes_lote/(\d{9})/$',
        views.detalhes_lote, name='detalhes_lote'),
]
