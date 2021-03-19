from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^ajax/stat_nivel/$', views.stat_nivel, name='stat_nivel'),

    url(r'^ajax/stat_niveis/([129]{1}.*)/$',
        views.stat_niveis, name='stat_niveis'),

    url(r'^busca/$', views.Busca.as_view(),
        name='busca'),
    url(r'^busca/(?P<busca>.+)/$', views.Busca.as_view(),
        name='busca__get'),

    url(r'^busca_modelo/$', views.BuscaModelo.as_view(),
        name='busca_modelo'),

    url(r'^custo/$',
        views.Custo.as_view(), name='custo'),
    url(r'^custo/(?P<nivel>.+)/(?P<ref>.+)/(?P<tamanho>.+)/(?P<cor>.+)/'
        r'(?P<alternativa>.+)/$',
        views.Custo.as_view(), name='custo__get'),

    url(r'^custo_ref/(?P<ref>[^/]+)?/?$',
        views.CustoRef.as_view(), name='custo_ref'),

    url(r'^estatistica/$', views.estatistica, name='estatistica'),

    url(r'^estr_estagio_de_insumo/$', views.EstrEstagioDeInsumo.as_view(),
        name='estr_estagio_de_insumo'),

    url(r'^gera_roteiros_padrao_ref/(?P<ref>[^/]+)?/(?P<quant>[^/]+)?/?$',
        views.GeraRoteirosPadraoRef.as_view(),
        name='gera_roteiros_padrao_ref'),

    url(r'^gtin/pesquisa/$',
        views.GtinPesquisa.as_view(), name='gtin_pesquisa'),
    url(r'^gtin/ref/$',
        views.RefGtinDefine.as_view(), name='gtin_ref'),
    url(r'^gtin/set/(?P<nivel>.+)/(?P<ref>.+)/(?P<tamanho>.+)/(?P<cor>.+)/$',
        views.SetGtinDefine.as_view(), name='gtin_set'),
    url(r'^gtin/set_next/(?P<nivel>.+)/(?P<ref>.+)/(?P<tamanho>.+)/(?P<cor>.+)/(?P<old_gtin>.+)/$',
        views.SetGtinDefine.as_view(), name='gtin_set_next'),
    url(r'^gtin/log/$',
        views.GtinLog.as_view(), name='gtin_log'),

    url(r'^gtinrange/$', views.GtinRangeListView.as_view(),
        name='gtinrange_changelist'),

    url(r'^gtinrange/add/$', views.GtinRangeCreateView.as_view(),
        name='gtinrange_add'),

    url(r'^gtinrange/(?P<pk>[^/]+)/$', views.GtinRangeUpdateView.as_view(),
        name='gtinrange_change'),

    url(r'^gtinrange/del/(?P<pk>[^/]+)/$', views.GtinRangeDeleteView.as_view(),
        name='gtinrange_delete'),

    url(r'^hist_narrativa/$', views.HistNarrativa.as_view(),
        name='hist_narrativa'),

    url(r'^info_xml/$', views.InfoXml.as_view(), name='info_xml'),
    url(r'^info_xml/(?P<ref>.+)/$',
        views.InfoXml.as_view(), name='info_xml__get'),

    url(r'^lista_item_n1_sem_preco_medio/$',
        views.lista_item_n1_sem_preco_medio,
        name='lista_item_n1_sem_preco_medio'),

    url(r'^modelo/$', views.Modelo.as_view(), name='modelo'),
    url(r'^modelo/(?P<modelo>.+)/$', views.Modelo.as_view(),
        name='modelo__get'),

    url(r'^multiplas_colecoes/$', views.MultiplasColecoes.as_view(),
        name='multiplas_colecoes'),

    url(r'^por_cliente/$', views.PorCliente.as_view(), name='por_cliente'),
    url(r'^por_cliente/(?P<cliente>.+)/$',
        views.PorCliente.as_view(), name='por_cliente__get'),

    url(r'^ref/$', views.Ref.as_view(), name='ref'),
    url(r'^ref/(?P<ref>.+)/$', views.Ref.as_view(), name='ref__get'),

    url(r'^roteiros_padrao_ref/(?P<ref>[^/]+)?/?$',
        views.RoteirosPadraoRef.as_view(), name='roteiros_padrao_ref'),

]
