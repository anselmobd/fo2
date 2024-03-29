from django.urls import path, re_path

from lotes.views.corte import (
    ajax_marca_op_cortada,
    envio_insumo,
    gera_pedido_op,
    informa_nf_envio,
    marca_op_cortada,
    pedidos_gerados,
    romaneio_corte,
)


def name(name):
    return f"corte-{name}"


urlpatterns = [
    path(
        "ajax_marca_op_cortada/<int:op>/",
        ajax_marca_op_cortada.AjaxMarcaOpCortadaView.as_view(),
        name=name('ajax_marca_op_cortada'),
    ),
    path(
        "envio_insumo/",
        envio_insumo.EnvioInsumo.as_view(),
        name=name('envio_insumo'),
    ),
    path(
        "gera_pedido_op/",
        gera_pedido_op.GeraPedidoOpView.as_view(),
        name=name('gera_pedido_op'),
    ),
    re_path(
        r"^informa_nf_envio/(?P<empresa>[0-9]+)/(?P<nf>[0-9]+)/"
        r"(?P<nf_ser>[0-9]+)/(?P<cnpj>[^/]+)/$",
        informa_nf_envio.InformaNfEnvio.as_view(),
        name=name('informa_nf_envio'),
    ),
    re_path(
        r"^marca_op_cortada/(?P<data>[^/]+)?$",
        marca_op_cortada.MarcaOpCortadaView.as_view(),
        name=name('marca_op_cortada'),
    ),
    path(
        "pedidos_gerados/",
        pedidos_gerados.PedidosGeradosView.as_view(),
        name=name('pedidos_gerados'),
    ),
    path(
        "romaneio_corte/",
        romaneio_corte.RomaneioCorte.as_view(),
        name=name('romaneio_corte'),
    ),
]
