from django.urls import re_path

from . import views
from .views import (
    busca_pedido,
    ot_pesar,
    pendente,
    producao,
)


app_name = 'beneficia'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    re_path(r'^ob/$', views.Ob.as_view(), name='ob'),
    re_path(r'^ob/(?P<ob>\d+)/$', views.Ob.as_view(), name='ob__get'),

    re_path(r'^busca_ob/$', views.BuscaOb.as_view(), name='busca_ob'),

    re_path(
        r'^busca_pedido/$',
        busca_pedido.BuscaPedido.as_view(),
        name='busca_pedido'
    ),

    re_path(r'^ot/$', views.Ot.as_view(), name='ot'),
    re_path(r'^ot/(?P<ot>\d+)/$', views.Ot.as_view(), name='ot__get'),

    re_path(r'^ot_pesar/$', ot_pesar.OtPesar.as_view(), name='ot_pesar'),

    re_path(r'^pendente/$', pendente.Pendente.as_view(), name='pendente'),

    re_path(r'^producao/$', producao.Producao.as_view(), name='producao'),

    re_path(r'^receita/(?P<receita>.+)?/?$', views.Receita.as_view(), name='receita'),

    re_path(r'^receita_estrutura/(?P<item>.+)?/?$', views.ReceitaEstrutura.as_view(), name='receita_estrutura'),
]
