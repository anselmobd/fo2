from pprint import pprint

from base.forms import custom
from base.forms import fields


class ModeloForm(
        custom.O2BaseForm,
        fields.O2FieldModeloForm):

    class Meta:
        autofocus_field = 'modelo'


def MountModeloForm():
    return MountForm(
        'deposito',
        autofocus_field='deposito'
    )


def MountForm(*args, **kwargs):
    '''
        args: são os inputs do form
            - string: referência a uma classe em classes (abaixo)
        kwargs: são atributos da subclasse Meta do form
    '''
    classes = {
        'deposito': {
            'class': fields.O2FieldDepositoForm,
        }
    }

    superclasses = custom.O2BaseForm,
    for field in args:
        superclasses += classes[field]['class'],

    Meta = type('MountedMeta', (object, ), kwargs)

    return type(
        "MountedDepositoForm",
        superclasses,
        {'Meta': Meta, }
    )
