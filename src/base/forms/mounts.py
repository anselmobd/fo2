from base.forms import custom
from base.forms import fields


def MountForm(*args, **kwargs):
    '''
        args: são os inputs do form
            - string: referência a uma classe em classes (abaixo)
        kwargs: são atributos da subclasse Meta do form
    '''
    classes = {
        'deposito': fields.O2FieldDepositoForm,
        'pedido': fields.O2FieldPedidoForm,
    }

    superclasses = custom.O2BaseForm,
    for field in args:
        superclasses += classes[field],

    Meta = type('MountedMeta', (object, ), kwargs)

    return type(
        "MountedDepositoForm",
        superclasses,
        {'Meta': Meta, }
    )
