from django.urls import path, re_path

from lotes.views.corte import (
    pedidos_gerados,
)

urlpatterns = [

    path(
        'pedidos_gerados/',
        pedidos_gerados.PedidosGeradosView.as_view(),
        name='corte-pedidos_gerados',
    ),

]
