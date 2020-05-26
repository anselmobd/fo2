from pprint import pprint

from base.forms.mount_forms import MountForm


DepositoForm = MountForm(
    'deposito',
    autofocus_field='deposito'
)

ModeloForm = MountForm(
    'modelo',
    autofocus_field='modelo',
    required_fields=['modelo'],
)

PedidoForm = MountForm(
    'pedido',
    autofocus_field='pedido'
)
