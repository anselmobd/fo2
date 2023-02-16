from pprint import pprint

from base.forms import mount_fields

from systextil.models import Colecao


class Fields2():

    @property
    def Modelo(self):
        return mount_fields.MountIntegerFieldForm(
            'modelo',
            attrs={
                'min_value': 1,
                'max_value': 99999,
            },
            widget_attrs={'size': 5},
        )

    @property
    def Pedido(self):
        return mount_fields.MountCharFieldForm(
            'pedido',
            widget_attrs={
                'size': 6,
                'pattern': "[0-9]{1,6}",
                'onkeypress': "o2PreventNonNumInput(event);",
                'onkeydown': "o2OnEnterCleanNonNumInputAndStay(event);",
                'onblur': "o2CleanNonNumKeys(event);",
                'oninvalid': "this.setCustomValidity('Apenas números. Até 6 dígitos.');",
                'oninput': "this.setCustomValidity('');",
            },
        )

    @property
    def Deposito(self):
        return mount_fields.MountIntegerFieldForm(
            'deposito',
            attrs={
                'label': 'Depósito',
                'min_value': 0,
                'max_value': 999,
            },
            widget_attrs={'size': 3},
        )

    @property
    def Colecao(self):
        return mount_fields.MountModelChoiceForm(
            'colecao',
            attrs={
                'label': 'Coleção',
                'required': False,
                'queryset': Colecao.objects.all().order_by('colecao'),
                'empty_label': "(Todas)",
            },
        )

    @property
    def Referencia(self):
        return mount_fields.MountCharFieldForm(
            'referencia',
            widget_attrs={
                'size': 5,
                'pattern': "[0-9A-Z]{5}",
                'onkeypress': "o2NoNonUpANumInput(event);",
                'onkeydown': "o2OnEnterCleanNonUpANumInputAndStay(event);",
                'onblur': "o2CleanNonUpANumKeys(event);",
                'oninvalid': "this.setCustomValidity('Apenas letras e números. Com 5 caracteres.');",
                'oninput': "this.setCustomValidity('');",
            },
        )
