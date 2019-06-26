from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^ficha_cliente/$', views.FichaCliente.as_view(),
        name='ficha_cliente'),
    url(r'^ficha_cliente/(?P<cnpj>\d+)/$', views.FichaCliente.as_view(),
        name='ficha_cliente__get'),

    url(r'^vendas_cor/$', views.VendasPorCor.as_view(), name='vendas_cor'),

    url(r'^estoque_desejado/$',
        views.estoque.EstoqueDesejado.as_view(),
        name='estoque_desejado'),

    url(r'^ponderacao/$',
        views.estoque.Ponderacao.as_view(),
        name='ponderacao'),

]
