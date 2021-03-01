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
    fields=[
        {'name': 'deposito'},
        {'name': 'data_de',
         'type': 'date',
         'label': 'Data de embarque - De:'},
        {'name': 'data_ate',
         'type': 'date',
         'label': 'Até:'},
    ],
    autofocus_field='deposito',
    required_fields=['deposito'],
)

ReferenciaForm2 = MountForm(
    'referencia',
    autofocus_field='referencia',
    required_fields=['referencia'],
)
