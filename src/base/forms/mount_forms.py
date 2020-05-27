from pprint import pprint

from base.forms import (
    custom,
    fields2,
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
        fields = {field: {} for field in args}

    superclasses = custom.O2BaseForm,
    for field in fields:
        if fields[field] == {}:
            superclasses += field_classes[field],

    Meta = type('MountedMeta', (object, ), kwargs)

    return type(
        "MountedDepositoForm",
        superclasses,
        {'Meta': Meta, }
    )
