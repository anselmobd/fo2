from pprint import pprint

from base.forms.mount_forms import MountForm


class Forms2:

    @property
    def Deposito(self):
        return MountForm(
            'deposito',
            autofocus_field='deposito',
            required_fields=['deposito'],
        )

    @property
    def Modelo(self):
        return MountForm(
            'modelo',
            autofocus_field='modelo',
            required_fields=['modelo'],
        )

    @property
    def Pedido(self):
        return MountForm(
            'pedido',
            autofocus_field='pedido',
            required_fields=['pedido'],
        )

    @property
    def DepositoDatas(self):
        return MountForm(
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

    @property
    def DepositoColecaoDatas(self):
        return MountForm(
            fields=[
                {'name': 'deposito'},
                {'name': 'colecao'},
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

    @property
    def Referencia(self):
        return MountForm(
            'referencia',
            autofocus_field='referencia',
            required_fields=['referencia'],
        )
