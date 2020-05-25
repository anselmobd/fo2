from pprint import pprint

from base.forms import custom
from base.forms import fields


def MountForm(*args, **kwargs):
    '''
        args: são os inputs do form
            - string: referência a uma classe em classes (abaixo)
        kwargs: são atributos da subclasse Meta do form
    '''

    field_classes = {
        'deposito': fields.O2FieldDepositoForm,
        'modelo': fields.O2FieldModeloForm,
        'pedido': fields.O2FieldPedidoForm,
    }

    superclasses = custom.O2BaseForm,
    for field in args:
        superclasses += field_classes[field],

    Meta = type('MountedMeta', (object, ), kwargs)

    return type(
        "MountedDepositoForm",
        superclasses,
        {'Meta': Meta, }
    )
