from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^posicao_estoque/$', views.PosicaoEstoque.as_view(),
        name='posicao_estoque'),

    url(r'^valor_mp/$', views.ValorMp.as_view(), name='valor_mp'),

    url(r'^inventario_expedicao/$', views.InventarioExpedicao.as_view(),
        name='inventario_expedicao'),

    url(r'^referencia_deposito/$', views.ReferenciaDeposito.as_view(),
        name='referencia_deposito'),

    url(r'^mostra_estoque/(?P<deposito>[^/]+)/(?P<ref>[^/]+)/'
        r'(?P<modelo>[^/]+)?/?$',
        views.MostraEstoque.as_view(), name='mostra_estoque__get'),

    url(r'^zera_estoque/(?P<deposito>[^/]+)/(?P<ref>[^/]+)/'
        r'(?P<cor>[^/]+)/(?P<tam>[^/]+)/$',
        views.ZeraEstoque.as_view(), name='zera_estoque__get'),
    url(r'^zera_estoque/(?P<deposito>[^/]+)/(?P<ref>[^/]+)/'
        r'(?P<cor>[^/]+)/(?P<tam>[^/]+)/(?P<conf_hash>[^/]+)/$',
        views.ZeraEstoque.as_view(), name='zera_estoque__get'),

    url(r'^edita_estoque/(?P<deposito>[^/]+)/(?P<ref>[^/]+)/'
        r'(?P<cor>[^/]+)/(?P<tam>[^/]+)/$',
        views.EditaEstoque.as_view(), name='edita_estoque__get'),
    url(r'^edita_estoque/(?P<deposito>[^/]+)/(?P<ref>[^/]+)/'
        r'(?P<cor>[^/]+)/(?P<tam>[^/]+)/(?P<qtd>[^/]+)/$',
        views.EditaEstoque.as_view(), name='edita_estoque__get'),
    url(r'^edita_estoque/(?P<deposito>[^/]+)/(?P<ref>[^/]+)/'
        r'(?P<cor>[^/]+)/(?P<tam>[^/]+)/(?P<qtd>[^/]+)/(?P<conf_hash>[^/]+)/$',
        views.EditaEstoque.as_view(), name='edita_estoque__get'),

    url(r'^executa_ajuste/(?P<dep>[^/]+)/(?P<ref>[^/]+)/'
        r'(?P<cor>[^/]+)/(?P<tam>[^/]+)/(?P<ajuste>[^/]+)/(?P<trail>[^/]+)/$',
        views.executa_ajuste, name='executa_ajuste'),

]
