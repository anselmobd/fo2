from pprint import pprint

from base.forms import mount_fields


O2FieldModeloForm2 = mount_fields.MountIntegerFieldForm(
    'modelo',
    attrs={
        'min_value': 1,
        'max_value': 9999,
    },
    widget_attrs={'size': 4},
)


O2FieldPedidoForm2 = mount_fields.MountIntegerFieldForm(
    'pedido',
    attrs={
        'min_value': 1,
        'max_value': 999999,
    },
    widget_attrs={'size': 6},
)
