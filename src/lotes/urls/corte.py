from django.urls import path

from lotes.views.corte import (
    ajax_marca_op_cortada,
    envio_insumo,
    pedidos_gerados,
)

urlpatterns = [

    path(
        'ajax_marca_op_cortada/<int:op>/',
        ajax_marca_op_cortada.AjaxMarcaOpCortadaView.as_view(),
        name='corte-ajax_marca_op_cortada',
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
