from pprint import pprint

from base.forms import (
    custom,
    fields2,
    mount_fields,
)


def MountForm(*args, **kwargs):
    '''
        args: são os inputs do form
            - string: referência a uma classe em classes (abaixo)
        kwargs: são atributos da subclasse Meta do form
    '''

    field_classes = {
        'deposito': fields2.O2FieldDepositoForm2,
        'modelo': fields2.O2FieldModeloForm2,
        'pedido': fields2.O2FieldPedidoForm2,
        'referencia': fields2.O2FieldReferenciaForm2,
    }

    if 'fields' in kwargs:
        fields = kwargs.pop('fields')
    else:
        fields = [{'name': name} for name in args]

    order_fields = []
    superclasses = custom.O2BaseForm,

    for field in fields:
        name = field.pop('name')
        order_fields.append(name)

        if field == {}:
            field_class = field_classes[name]
        else:
            attrs = {}
            if 'label' in field:
                attrs.update({'label': field['label']})
            if field['type'] == 'date':
                field_class = mount_fields.MountDateFieldForm(
                    name,
                    attrs=attrs,
                )
        superclasses += field_class,

    kwargs['order_fields'] = order_fields
    Meta = type('MountedMeta', (object, ), kwargs)

    return type(
        "MountedDepositoForm",
        superclasses,
        {'Meta': Meta, }
    )
