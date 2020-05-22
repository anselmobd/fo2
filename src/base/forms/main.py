from pprint import pprint

from base.forms.mounts import MountForm


ModeloForm = MountForm(
    'modelo',
    autofocus_field='modelo'
)

PedidoForm = MountForm(
    'pedido',
    autofocus_field='pedido'
)
