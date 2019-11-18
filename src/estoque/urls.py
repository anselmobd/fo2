from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^posicao_estoque/$', views.PorDeposito.as_view(),
        name='posicao_estoque'),

    url(r'^valor_mp/$', views.ValorMp.as_view(), name='valor_mp'),

    url(r'^inventario_expedicao/$', views.InventarioExpedicao.as_view(),
        name='inventario_expedicao'),
]
