from pprint import pprint

from base.forms import mount_fields

from systextil.models import Colecao


O2FieldModeloForm2 = mount_fields.MountIntegerFieldForm(
    'modelo',
    attrs={
        'min_value': 1,
        'max_value': 99999,
    },
    widget_attrs={'size': 5},
)


O2FieldPedidoForm2 = mount_fields.MountCharFieldForm(
    'pedido',
    widget_attrs={
        'size': 6,
        'pattern': "[0-9]{1,6}",
        'onkeypress': "o2PreventNonNumericalInput(event);",
        'onkeydown': "o2CleanNonNumericalInputAndStay(event);",
        'onblur': "o2CleanNonNumericalKeys(event);",
        'oninvalid': "this.setCustomValidity('Só números. Até 6 dígitos.');",
        'oninput': "this.setCustomValidity('');",
    },
)

O2FieldDepositoForm2 = mount_fields.MountIntegerFieldForm(
    'deposito',
    attrs={
        'label': 'Depósito',
        'min_value': 0,
        'max_value': 999,
    },
    widget_attrs={'size': 3},
)

O2FieldColecaoForm2 = mount_fields.MountModelChoiceForm(
    'colecao',
    attrs={
        'label': 'Coleção',
        'required': False,
        'queryset': Colecao.objects.all().order_by('colecao'),
        'empty_label': "(Todas)",
    },
)

O2FieldReferenciaForm2 = mount_fields.MountCharFieldForm(
    'referencia',
    widget_attrs={'size': 5},
)

