from django.urls import path

from lotes.views.corte import (
    envio_insumo,
    pedidos_gerados,
)

urlpatterns = [

    path(
        'envio_insumo/',
        envio_insumo.EnvioInsumo.as_view(),
        name='corte-envio_insumo',
    ),

    path(
        'pedidos_gerados/',
        pedidos_gerados.PedidosGeradosView.as_view(),
        name='corte-pedidos_gerados',
    ),

]
