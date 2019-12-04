from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^posicao_estoque/$', views.PorDeposito.as_view(),
        name='posicao_estoque'),

    url(r'^valor_mp/$', views.ValorMp.as_view(), name='valor_mp'),

    url(r'^inventario_expedicao/$', views.InventarioExpedicao.as_view(),
        name='inventario_expedicao'),

    url(r'^referencia_deposito/$', views.ReferenciaDeposito.as_view(),
        name='referencia_deposito'),

    url(r'^edita_estoque/(?P<deposito>.+)/(?P<ref>.+)/$',
        views.EditaEstoque.as_view(), name='edita_estoque__get'),

    url(r'^ajusta_estoque/(?P<deposito>[^/]+)/(?P<ref>[^/]+)/'
        r'(?P<cor>[^/]+)/(?P<tam>[^/]+)/(?P<qtd>0)/$',
        views.ZeraEstoque.as_view(), name='ajusta_estoque__get'),

    url(r'^ajusta_estoque/(?P<deposito>[^/]+)/(?P<ref>[^/]+)/'
        r'(?P<cor>[^/]+)/(?P<tam>[^/]+)/(?P<qtd>[^/]+)/$',
        views.AjustaEstoque.as_view(), name='ajusta_estoque__get'),

    url(r'^ajusta_estoque/(?P<deposito>[^/]+)/(?P<ref>[^/]+)/'
        r'(?P<cor>[^/]+)/(?P<tam>[^/]+)/(?P<qtd>[^/]+)/'
        r'(?P<conf_hash>[^/]+)/$',
        views.AjustaEstoque.as_view(), name='ajusta_estoque__get'),
]
