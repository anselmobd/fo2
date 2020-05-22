from pprint import pprint

from base.forms import custom
from base.forms import fields


class ModeloForm(
        custom.O2BaseForm,
        fields.O2FieldModeloForm):

    class Meta:
        autofocus_field = 'modelo'


def MountForm(*args, **kwargs):
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
