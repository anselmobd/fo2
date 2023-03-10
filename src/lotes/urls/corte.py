from django.urls import path

from lotes.views.corte import (
    envio_insumo,
    marca_op_cortada,
    pedidos_gerados,
)

urlpatterns = [

    path(
        'ajax/marca_op_cortada/<int:op>/',
        marca_op_cortada.MarcaOpCortada.as_view(),
        name='corte-marca_op_cortada',
    ),

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
