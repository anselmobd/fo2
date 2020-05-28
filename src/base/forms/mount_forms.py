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
    }

    if 'fields' in kwargs:
        fields = kwargs.pop('fields')
    else:
        fields = [{field: {}} for field in args]

    superclasses = custom.O2BaseForm,
    kwargs['order_fields'] = []

    for field in fields:
        field_name = list(field.keys())[0]
        kwargs['order_fields'].append(field_name)

        field_conf = field[field_name]
        if field_conf == {}:
            field_class = field_classes[field_name]
        else:
            attrs = {}
            if 'label' in field_conf:
                attrs.update({'label': field_conf['label']})
            if field_conf['type'] == 'date':
                field_class = mount_fields.MountDateFieldForm(
                    field_name,
                    attrs=attrs,
                )
        superclasses += field_class,

    Meta = type('MountedMeta', (object, ), kwargs)

    return type(
        "MountedDepositoForm",
        superclasses,
        {'Meta': Meta, }
    )
