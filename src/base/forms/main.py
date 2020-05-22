from pprint import pprint

from base.forms.mounts import MountForm


DepositoForm = MountForm(
    'deposito',
    autofocus_field='deposito'
)

ModeloForm = MountForm(
    'modelo',
    autofocus_field='modelo'
)

PedidoForm = MountForm(
    'pedido',
    autofocus_field='pedido'
)
