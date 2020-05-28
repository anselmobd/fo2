from pprint import pprint

from base.forms.mount_forms import MountForm


DepositoForm2 = MountForm(
    'deposito',
    autofocus_field='deposito',
    required_fields=['deposito'],
)

ModeloForm2 = MountForm(
    'modelo',
    autofocus_field='modelo',
    required_fields=['modelo'],
)

PedidoForm2 = MountForm(
    'pedido',
    autofocus_field='pedido',
    required_fields=['pedido'],
)

DepositoDatasForm2 = MountForm(
    order_fields=['deposito', 'data_de', 'data_ate'],
    fields=[
        {'deposito': {}},
        {'data_de': {'type': 'date', 'label': 'Data de embarque - De:'}},
        {'data_ate': {'type': 'date', 'label': 'Até:'}},
    ],
    autofocus_field='deposito',
    required_fields=['deposito'],
)
