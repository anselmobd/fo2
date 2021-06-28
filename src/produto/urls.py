from django.urls import re_path

from . import views


app_name = 'produto'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    re_path(r'^ajax/stat_nivel/$', views.stat_nivel, name='stat_nivel'),

    re_path(r'^ajax/stat_niveis/([129]{1}.*)/$',
        views.stat_niveis, name='stat_niveis'),

    re_path(r'^busca/$', views.Busca.as_view(),
        name='busca'),
    re_path(r'^busca/(?P<busca>.+)/$', views.Busca.as_view(),
        name='busca__get'),

    re_path(r'^busca_modelo/$', views.BuscaModelo.as_view(),
        name='busca_modelo'),

    re_path(r'^custo/$',
        views.Custo.as_view(), name='custo'),
    re_path(r'^custo/(?P<nivel>.+)/(?P<ref>.+)/(?P<tamanho>.+)/(?P<cor>.+)/'
        r'(?P<alternativa>.+)/$',
        views.Custo.as_view(), name='custo__get'),

    re_path(r'^custo_ref/(?P<ref>[^/]+)?/?$',
        views.CustoRef.as_view(), name='custo_ref'),

    re_path(r'^estatistica/$', views.estatistica, name='estatistica'),

    re_path(r'^estr_estagio_de_insumo/$', views.EstrEstagioDeInsumo.as_view(),
        name='estr_estagio_de_insumo'),

    re_path(r'^ficha_tecnica/$', views.FichaTecnica.as_view(),
        name='ficha_tecnica'),

    re_path(r'^gera_roteiros_padrao_ref/(?P<ref>[^/]+)?/(?P<quant>[^/]+)?/?$',
        views.GeraRoteirosPadraoRef.as_view(),
        name='gera_roteiros_padrao_ref'),

    re_path(r'^gtin/pesquisa/$',
        views.GtinPesquisa.as_view(), name='gtin_pesquisa'),
    re_path(r'^gtin/ref/$',
        views.RefGtinDefine.as_view(), name='gtin_ref'),
    re_path(r'^gtin/set/(?P<nivel>.+)/(?P<ref>.+)/(?P<tamanho>.+)/(?P<cor>.+)/$',
        views.SetGtinDefine.as_view(), name='gtin_set'),
    re_path(r'^gtin/set_next/(?P<nivel>.+)/(?P<ref>.+)/(?P<tamanho>.+)/(?P<cor>.+)/(?P<old_gtin>.+)/$',
        views.SetGtinDefine.as_view(), name='gtin_set_next'),
    re_path(r'^gtin/log/$',
        views.GtinLog.as_view(), name='gtin_log'),

    re_path(r'^gtinrange/$', views.GtinRangeListView.as_view(),
        name='gtinrange_changelist'),

    re_path(r'^gtinrange/add/$', views.GtinRangeCreateView.as_view(),
        name='gtinrange_add'),

    re_path(r'^gtinrange/(?P<pk>[^/]+)/$', views.GtinRangeUpdateView.as_view(),
        name='gtinrange_change'),

    re_path(r'^gtinrange/del/(?P<pk>[^/]+)/$', views.GtinRangeDeleteView.as_view(),
        name='gtinrange_delete'),

    re_path(r'^hist_narrativa/$', views.HistNarrativa.as_view(),
        name='hist_narrativa'),

    re_path(r'^info_xml/$', views.InfoXml.as_view(), name='info_xml'),
    re_path(r'^info_xml/(?P<ref>.+)/$',
        views.InfoXml.as_view(), name='info_xml__get'),

    re_path(r'^lista_item_n1_sem_preco_medio/$',
        views.lista_item_n1_sem_preco_medio,
        name='lista_item_n1_sem_preco_medio'),

    re_path(r'^modelo/$', views.Modelo.as_view(), name='modelo'),
    re_path(r'^modelo/(?P<modelo>.+)/$', views.Modelo.as_view(),
        name='modelo__get'),

    re_path(r'^multiplas_colecoes/$', views.MultiplasColecoes.as_view(),
        name='multiplas_colecoes'),

    re_path(r'^por_cliente/$', views.PorCliente.as_view(), name='por_cliente'),
    re_path(r'^por_cliente/(?P<cliente>.+)/$',
        views.PorCliente.as_view(), name='por_cliente__get'),

    re_path(r'^ref/$', views.Ref.as_view(), name='ref'),
    re_path(r'^ref/(?P<ref>.+)/$', views.Ref.as_view(), name='ref__get'),

    re_path(r'^roteiros_padrao_ref/(?P<ref>[^/]+)?/?$',
        views.RoteirosPadraoRef.as_view(), name='roteiros_padrao_ref'),

]
