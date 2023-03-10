from django.urls import path, re_path

from lotes.views.corte import (
    ajax_marca_op_cortada,
    envio_insumo,
    gera_pedido_op,
    marca_op_cortada,
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
        'gera_pedido_op/',
        gera_pedido_op.GeraPedidoOpView.as_view(),
        name='corte-gera_pedido_op',
    ),
    re_path(
        r'^marca_op_cortada/(?P<data>[^/]+)?$',
        marca_op_cortada.MarcaOpCortadaView.as_view(),
        name='corte-marca_op_cortada',
    ),
    path(
        'pedidos_gerados/',
        pedidos_gerados.PedidosGeradosView.as_view(),
        name='corte-pedidos_gerados',
    ),
]
